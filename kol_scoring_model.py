"""
KOL 影响力光谱评分模型
采用多维度加权评分体系，综合评估 KOL 的真实影响力

评分维度:
1. 互动率 (Engagement Rate) — 权重 35%
2. 内容质量 (Content Consistency) — 权重 15%
3. 商业价值 (Commerce Potential) — 权重 10%
4. 涨粉速度 (Follower Growth) — 权重 15%
5. 粉丝规模 (Follower Size) — 权重 10%
6. 受众质量 (Audience Quality) — 权重 15%

✨ 创新点: 引入 "影响力光谱" 概念，将 KOL 分为四个象限:
   - 恒星 KOL (高内容质量 × 高商业价值)
   - 新星 KOL (高内容质量 × 低商业价值)
   - 商业大V (低内容质量 × 高商业价值)
   - 小众玩家 (低内容质量 × 低商业价值)
"""
import os, json
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# 默认权重配置 (可通过 .env 自定义)
WEIGHTS = {
    "engagement_rate": float(os.getenv("KOL_WEIGHT_ENGAGEMENT_RATE", 0.35)),
    "content_consistency": float(os.getenv("KOL_WEIGHT_CONTENT_CONSISTENCY", 0.15)),
    "commerce_potential": float(os.getenv("KOL_WEIGHT_COMMERCE_POTENTIAL", 0.10)),
    "follower_growth": float(os.getenv("KOL_WEIGHT_FOLLOWER_GROWTH", 0.15)),
    "followers": float(os.getenv("KOL_WEIGHT_FOLLOWERS", 0.10)),
    "audience_quality": float(os.getenv("KOL_WEIGHT_AUDIENCE_QUALITY", 0.15)),
}

def minmax_norm(values):
    """Min-Max 归一化到 0–100"""
    lo, hi = values.min(), values.max()
    if hi - lo < 1e-9:
        return np.full_like(values, 50.0)
    return (values - lo) / (hi - lo) * 100

def log_norm(values):
    """对数归一化（适合粉丝数这类长尾指标）"""
    logged = np.log1p(np.maximum(values, 1))
    lo, hi = logged.min(), logged.max()
    if hi - lo < 1e-9:
        return np.full_like(values, 50.0)
    return (logged - lo) / (hi - lo) * 100

def compute_influence_spectrum(scores_df):
    """计算影响力光谱坐标 (内容质量分 × 商业价值分)"""
    content_quality = (
        scores_df["score_engagement"] * 0.5 +
        scores_df["score_content_freq"] * 0.3 +
        scores_df["score_views"] * 0.2
    )
    commercial_value = (
        scores_df["score_commerce"] * 0.4 +
        scores_df["score_followers"] * 0.3 +
        scores_df["score_audience"] * 0.3
    )
    return content_quality, commercial_value

def score_kols(ig_data=None, tt_data=None, weights=None):
    """
    对 KOL 进行综合评分
    ig_data: Instagram 数据列表
    tt_data: TikTok 数据列表
    weights: 自定义权重字典
    """
    if weights is None:
        weights = WEIGHTS
    
    # 合并数据
    records = []
    if ig_data:
        for d in ig_data:
            records.append({
                "username": d["username"],
                "platform": "Instagram",
                "followers": d["followers"],
                "engagement_rate": d["engagement_rate"],
                "avg_likes": d["avg_likes"],
                "posts_count": d["posts_count"],
                "avg_views": 0,
                "products_count": 0,
                "is_verified": d["is_verified"],
            })
    if tt_data:
        for d in tt_data:
            records.append({
                "username": d["username"],
                "platform": "TikTok",
                "followers": d["followers"],
                "engagement_rate": (d["avg_likes"] / max(d["followers"], 1)) * 100 if d["followers"] else 0,
                "avg_likes": d["avg_likes"],
                "posts_count": d["videos"],
                "avg_views": d["avg_views"],
                "products_count": 0,
                "is_verified": d["verified"],
            })
    
    df = pd.DataFrame(records)
    if df.empty:
        return df
    
    # 按 username 聚合
    df_agg = df.groupby("username").agg({
        "followers": "max",
        "engagement_rate": "max",
        "avg_likes": "max",
        "avg_views": "max",
        "posts_count": "max",
        "products_count": "max",
        "is_verified": "max",
        "platform": lambda x: "+".join(sorted(set(x))),
    }).reset_index()
    
    # 归一化
    df_agg["score_engagement"] = minmax_norm(df_agg["engagement_rate"].values)
    df_agg["score_followers"] = log_norm(df_agg["followers"].values)
    df_agg["score_views"] = log_norm(df_agg["avg_views"].values)
    df_agg["score_commerce"] = minmax_norm(df_agg["products_count"].values)
    df_agg["score_content_freq"] = minmax_norm(df_agg["posts_count"].values)
    df_agg["score_audience"] = minmax_norm(df_agg["is_verified"].astype(float).values)
    
    # 加权总分
    df_agg["kol_score"] = (
        df_agg["score_engagement"] * weights["engagement_rate"] +
        df_agg["score_content_freq"] * weights["content_consistency"] +
        df_agg["score_commerce"] * weights["commerce_potential"] +
        df_agg["score_followers"] * weights["followers"] +
        df_agg["score_views"] * weights["follower_growth"] +
        df_agg["score_audience"] * weights["audience_quality"]
    )
    
    # 计算影响力光谱
    cq, cv = compute_influence_spectrum(df_agg)
    df_agg["content_quality"] = cq
    df_agg["commercial_value"] = cv
    
    # 象限分类
    def classify(row):
        if row["content_quality"] >= 50 and row["commercial_value"] >= 50:
            return "Star KOL（明星级）"
        elif row["content_quality"] >= 50:
            return "Rising Star（新星）"
        elif row["commercial_value"] >= 50:
            return "Commercial Gun（商业大V）"
        else:
            return "Niche Player（小众玩家）"
    
    df_agg["spectrum_category"] = df_agg.apply(classify, axis=1)
    df_agg.sort_values("kol_score", ascending=False, inplace=True)
    df_agg["rank"] = range(1, len(df_agg) + 1)
    
    return df_agg

if __name__ == "__main__":
    # 示例: 使用示例数据运行
    sample_ig = [
        {"username": "emma_c", "followers": 450000, "engagement_rate": 4.8, "avg_likes": 21600, "posts_count": 320, "is_verified": True},
    ]
    sample_tt = [
        {"username": "emma_c", "followers": 890000, "avg_likes": 52000, "videos": 180, "avg_views": 450000, "verified": True},
    ]
    result = score_kols(sample_ig, sample_tt)
    print(result[["rank", "username", "kol_score", "spectrum_category", "platform"]])
    result.to_csv("kol_ranking.csv", index=False, encoding="utf-8-sig")
