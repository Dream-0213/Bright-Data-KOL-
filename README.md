# Bright Data KOL Data Pipeline

基于 Bright Data API 的海外社媒 (Instagram + TikTok) 网红数据采集与分析工具。

## ✨ 核心功能

- **Instagram 数据采集**: 粉丝数、互动率、帖子频率、认证状态等
- **TikTok 数据采集**: 播放量、涨粉趋势、带货数据等
- **KOL 影响力光谱评分**: 多维度加权评分模型，包含 6+ 个评价维度
- **数据导出**: 支持 CSV / Excel / Google Sheets
- **四象限分类**: 将 KOL 分为明星级、新星、商业大V、小众玩家

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 Bright Data API Token。

### 3. 创建采集器 Zone

在 Bright Data 控制台创建以下 Zone:
- `instagram_profiles` — Instagram Profile Scraper
- `tiktok_profiles` — TikTok Profile Scraper

### 4. 采集数据

```bash
python scripts/instagram_scraper.py
python scripts/tiktok_scraper.py
```

### 5. 运行评分模型

```bash
python scripts/kol_scoring_model.py
```

### 6. 导出报告

```bash
python scripts/export_report.py
```

## 📊 评分模型说明

| 维度 | 权重 | 说明 |
|------|------|------|
| 互动率 | 35% | 评论区互动 / 粉丝数 × 100 |
| 内容质量 | 15% | 内容发布频率 × 回复率 |
| 商业价值 | 10% | 带货商品数 / 商业合作历史 |
| 涨粉速度 | 15% | 近期播放量 / 粉丝增长趋势 |
| 粉丝规模 | 10% | 对数归一化的粉丝总数 |
| 受众质量 | 15% | 粉丝真实性评分 / 认证状态 |

## 🔗 相关链接

- [Bright Data 官网](https://brightdata.com/)
- [Bright Data Web Scraper API](https://brightdata.com/products/web-scraper)
- [Bright Data MCP](https://brightdata.com/products/mcp)
- [Bright Data GitHub](https://github.com/brightdata/brightdata-mcp)

## 📄 许可

MIT
