"""
Instagram Profile Scraper - Bright Data API
采集 Instagram 博主主页数据，包括粉丝数、互动率、帖子频率等
"""
import os, json, time, requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BRIGHTDATA_API_TOKEN")
API_BASE = "https://api.brightdata.com/dca"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def trigger_ig_collection(usernames, zone="instagram_profiles"):
    inputs = [{"url": f"https://www.instagram.com/{u}/"} for u in usernames]
    resp = requests.post(
        f"{API_BASE}/trigger", headers=HEADERS,
        json={"zone": zone, "input": inputs}, timeout=60
    )
    resp.raise_for_status()
    return resp.json()["snapshot_id"]

def poll_until_done(snapshot_id, interval=10, max_attempts=60):
    for i in range(max_attempts):
        time.sleep(interval)
        resp = requests.get(
            f"{API_BASE}/snapshot/{snapshot_id}", headers=HEADERS, timeout=30
        )
        snap = resp.json()
        phase = snap.get("phase")
        print(f"  Poll {i+1}/{max_attempts} — phase={phase}")
        if phase == "done":
            return snap
        if phase == "failed":
            raise RuntimeError(f"Task failed: {snap}")
    raise TimeoutError("Polling timeout")

def download_records(snapshot):
    records = snapshot.get("records", [])
    if records:
        return records
    sid = snapshot["snapshot_id"]
    resp = requests.get(
        f"{API_BASE}/snapshot/{sid}/download", headers=HEADERS, timeout=60
    )
    return resp.json() if isinstance(resp.json(), list) else []

def scrape_instagram_profiles(usernames, zone="instagram_profiles"):
    """一站式采集 Instagram 博主数据"""
    sid = trigger_ig_collection(usernames, zone)
    snap = poll_until_done(sid)
    data = download_records(snap)
    # 提取关键字段
    results = []
    for item in data:
        info = item.get("info", {})
        results.append({
            "platform": "Instagram",
            "username": info.get("username", ""),
            "full_name": info.get("full_name", ""),
            "followers": info.get("followers_count", 0),
            "following": info.get("following_count", 0),
            "posts_count": info.get("posts_count", 0),
            "is_verified": info.get("is_verified", False),
            "is_business": info.get("is_business_account", False),
            "category": info.get("category", ""),
            "biography": info.get("biography", ""),
            "engagement_rate": info.get("engagement_rate", 0),
            "avg_likes": info.get("avg_likes", 0),
            "avg_comments": info.get("avg_comments", 0),
        })
    return results

if __name__ == "__main__":
    targets = ["beauty_by_emma", "techwithjason", "fitness_with_luna"]
    data = scrape_instagram_profiles(targets)
    print(f"Scraped {len(data)} Instagram profiles")
    with open("instagram_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
