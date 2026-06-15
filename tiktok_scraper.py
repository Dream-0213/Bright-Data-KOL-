"""
TikTok Creator Scraper - Bright Data API
采集 TikTok 创作者数据，包括粉丝数、播放量、带货数据等
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

def trigger_tt_collection(usernames, zone="tiktok_profiles"):
    inputs = [{"url": f"https://www.tiktok.com/@{u}"} for u in usernames]
    resp = requests.post(
        f"{API_BASE}/trigger", headers=HEADERS,
        json={"zone": zone, "input": inputs}, timeout=60
    )
    resp.raise_for_status()
    return resp.json()["snapshot_id"]

def poll_tt(snapshot_id, interval=10, max_attempts=60):
    for i in range(max_attempts):
        time.sleep(interval)
        resp = requests.get(
            f"{API_BASE}/snapshot/{snapshot_id}", headers=HEADERS, timeout=30
        )
        snap = resp.json()
        if snap.get("phase") == "done":
            return snap
        if snap.get("phase") == "failed":
            raise RuntimeError(f"Task failed: {snap}")
        print(f"  Poll {i+1}/{max_attempts} — phase={snap.get('phase')}")
    raise TimeoutError("Polling timeout")

def download_tt(snapshot):
    records = snapshot.get("records", [])
    if records:
        return records
    sid = snapshot["snapshot_id"]
    resp = requests.get(
        f"{API_BASE}/snapshot/{sid}/download", headers=HEADERS, timeout=60
    )
    return resp.json() if isinstance(resp.json(), list) else []

def scrape_tiktok_profiles(usernames, zone="tiktok_profiles"):
    """一站式采集 TikTok 创作者数据"""
    sid = trigger_tt_collection(usernames, zone)
    snap = poll_tt(sid)
    data = download_tt(snap)
    results = []
    for item in data:
        info = item.get("info", {}).get("userInfo", {}).get("user", {})
        stats = item.get("info", {}).get("userInfo", {}).get("stats", {})
        results.append({
            "platform": "TikTok",
            "username": info.get("uniqueId", ""),
            "nickname": info.get("nickname", ""),
            "followers": stats.get("followerCount", 0),
            "following": stats.get("followingCount", 0),
            "hearts": stats.get("heartCount", 0),
            "videos": stats.get("videoCount", 0),
            "verified": info.get("verified", False),
            "bio": info.get("signature", ""),
            "avg_views": stats.get("avgViews", 0),
            "avg_likes": stats.get("avgLikes", 0),
            "avg_shares": stats.get("avgShares", 0),
        })
    return results

if __name__ == "__main__":
    targets = ["beauty_by_emma", "techwithjason", "fitness_with_luna"]
    data = scrape_tiktok_profiles(targets)
    print(f"Scraped {len(data)} TikTok profiles")
    with open("tiktok_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
