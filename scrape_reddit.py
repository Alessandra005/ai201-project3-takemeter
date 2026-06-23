"""
scrape_reddit.py — Collect r/movies posts for TakeMeter
Uses Reddit's public JSON API (no account, no credentials needed).

Usage:
    pip install requests
    python scrape_reddit.py

Output:
    reddit_raw.csv — unlabeled posts, ready for auto-labeling
"""

import requests
import csv
import time
import json

HEADERS = {"User-Agent": "takemeter-scraper/1.0 (research project)"}
OUTPUT_FILE = "reddit_raw.csv"

# ── Search queries targeting each label type ──────────────────────────────────
# We pull from several different query types to ensure variety across label classes.

FEEDS = [
    # Likely ANALYSIS posts — longer, argumentative, structured
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "cinematography analysis breakdown", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "essay argument why because structure", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "compared to trilogy director filmography", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},

    # Likely HOT_TAKE posts — contrarian, opinionated, bold claims
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "unpopular opinion overrated underrated", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "controversial take fight me disagree", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "worst best ever made all time", "sort": "top", "t": "year", "limit": 50, "restrict_sr": 1}},

    # Likely REACTION posts — news, trailers, just-watched
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "just watched first time seeing finally", "sort": "new", "t": "month", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "trailer reaction casting announced new movie", "sort": "new", "t": "month", "limit": 50, "restrict_sr": 1}},
    {"url": "https://www.reddit.com/r/movies/search.json",
     "params": {"q": "just saw theaters IMAX ending was", "sort": "new", "t": "month", "limit": 50, "restrict_sr": 1}},
]

# Also pull top posts generally (good mix of all types)
GENERAL_FEEDS = [
    {"url": "https://www.reddit.com/r/movies/top.json",
     "params": {"t": "month", "limit": 50}},
    {"url": "https://www.reddit.com/r/movies/hot.json",
     "params": {"limit": 50}},
]


def fetch_posts(url, params):
    """Fetch posts from Reddit JSON API with rate-limit handling."""
    posts = []
    after = None
    fetched = 0
    target = params.get("limit", 50)

    while fetched < target:
        p = dict(params)
        p["limit"] = min(100, target - fetched)
        if after:
            p["after"] = after

        try:
            r = requests.get(url, headers=HEADERS, params=p, timeout=15)
            if r.status_code == 429:
                print("  Rate limited — waiting 10s...")
                time.sleep(10)
                continue
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} — skipping")
                break
            data = r.json()
        except Exception as e:
            print(f"  Error: {e}")
            break

        children = data.get("data", {}).get("children", [])
        if not children:
            break

        for child in children:
            post = child.get("data", {})
            text = extract_text(post)
            if text:
                posts.append({
                    "id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "text": text,
                    "score": post.get("score", 0),
                    "url": "https://reddit.com" + post.get("permalink", ""),
                })

        fetched += len(children)
        after = data.get("data", {}).get("after")
        if not after:
            break
        time.sleep(1)  # Be polite

    return posts


def extract_text(post):
    """
    Build classifier text from a post.
    Prefer selftext (body) + title; fall back to title only.
    Filter out very short posts and non-text posts.
    """
    title = post.get("title", "").strip()
    body = post.get("selftext", "").strip()

    # Skip removed/deleted posts
    if body in ("[removed]", "[deleted]", ""):
        text = title
    else:
        # Combine title and body, truncate body to 500 chars to keep it manageable
        text = f"{title}\n\n{body[:500]}"

    # Skip if too short to be meaningful (< 30 chars)
    if len(text) < 30:
        return None

    # Skip if it's just a link post with no discussion value
    if post.get("is_video") or (post.get("url", "").endswith((".jpg", ".png", ".gif"))):
        return None

    return text


def deduplicate(posts):
    """Remove duplicate texts."""
    seen = set()
    unique = []
    for p in posts:
        key = p["text"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def main():
    all_posts = []

    print("Fetching targeted search feeds...")
    for feed in FEEDS:
        print(f"  {feed['params'].get('q', 'general')[:60]}...")
        posts = fetch_posts(feed["url"], feed["params"])
        print(f"    → {len(posts)} posts")
        all_posts.extend(posts)
        time.sleep(2)

    print("\nFetching general feeds...")
    for feed in GENERAL_FEEDS:
        posts = fetch_posts(feed["url"], feed["params"])
        print(f"  → {len(posts)} posts")
        all_posts.extend(posts)
        time.sleep(2)

    # Deduplicate
    all_posts = deduplicate(all_posts)
    print(f"\nTotal unique posts collected: {len(all_posts)}")

    # Save to CSV (no label yet — auto-labeling script handles that)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "text", "score", "url"])
        writer.writeheader()
        writer.writerows(all_posts)

    print(f"Saved to {OUTPUT_FILE}")
    print("\nNext step: run  python autolabel.py  to pre-label with Groq.")


if __name__ == "__main__":
    main()
