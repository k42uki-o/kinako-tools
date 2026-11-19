#!/usr/bin/env python3
"""FxTwitter public API helper.

Reads public X (Twitter) posts and profiles through api.fxtwitter.com.
No credential is needed or used.

Usage:
  fxtwitter.py tweet <x-post-url | status-id> [--user <screen_name>]
  fxtwitter.py user <screen_name>

Output is a compact JSON summary on stdout.
"""

import json
import re
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.fxtwitter.com"
TIMEOUT = 30


def fetch(path):
    request = urllib.request.Request(
        API_BASE + path,
        headers={"User-Agent": "muse-fxtwitter-connector/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(json.dumps({"error": f"HTTP {exc.code} for {path}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # network, timeout, bad JSON
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        sys.exit(1)


def parse_status_ref(ref):
    """Return (screen_name_or_None, status_id) from a URL or bare ID."""
    ref = ref.strip()
    match = re.search(r"(?:x\.com|twitter\.com|fxtwitter\.com|vxtwitter\.com)/"
                      r"([A-Za-z0-9_]+)/status/(\d+)", ref)
    if match:
        return match.group(1), match.group(2)
    match = re.search(r"/status/(\d+)", ref)
    if match:
        return None, match.group(1)
    if ref.isdigit():
        return None, ref
    print(json.dumps({"error": f"could not parse a status id from: {ref}"}),
          file=sys.stderr)
    sys.exit(2)


def media_urls(media):
    photos, videos = [], []
    if isinstance(media, dict):
        for item in media.get("photos") or []:
            if isinstance(item, dict) and item.get("url"):
                photos.append(item["url"])
        for item in media.get("videos") or []:
            if isinstance(item, dict) and item.get("url"):
                videos.append(item["url"])
    elif isinstance(media, list):
        for item in media:
            if isinstance(item, dict) and item.get("url"):
                if item.get("type") == "photo":
                    photos.append(item["url"])
                else:
                    videos.append(item["url"])
    return photos, videos


def summarize_tweet(tweet):
    author = tweet.get("author") or {}
    raw = tweet.get("raw_text") or {}
    photos, videos = media_urls(tweet.get("media"))
    summary = {
        "url": tweet.get("url"),
        "id": tweet.get("id"),
        "author_name": author.get("name"),
        "author_screen_name": author.get("screen_name"),
        "author_followers": author.get("followers"),
        "created_at": tweet.get("created_at"),
        "lang": tweet.get("lang"),
        "text": raw.get("text") or tweet.get("text"),
        "likes": tweet.get("likes"),
        "retweets": tweet.get("retweets"),
        "replies": tweet.get("replies"),
        "views": tweet.get("views"),
        "bookmarks": tweet.get("bookmarks"),
        "photos": photos,
        "videos": videos,
    }
    article = tweet.get("article")
    if isinstance(article, dict) and article:
        summary["article"] = {
            "title": article.get("title"),
            "note": "long-form article post. The API returns metadata only, "
                    "so read the body through the browser when needed.",
        }
    quote = tweet.get("quote")
    if isinstance(quote, dict) and quote:
        q_author = quote.get("author") or {}
        q_raw = quote.get("raw_text") or {}
        summary["quoted_tweet"] = {
            "author_screen_name": q_author.get("screen_name"),
            "text": q_raw.get("text") or quote.get("text"),
            "url": quote.get("url"),
        }
    return summary


def summarize_user(user):
    raw = user.get("raw_description") or {}
    return {
        "screen_name": user.get("screen_name"),
        "name": user.get("name"),
        "url": user.get("url"),
        "followers": user.get("followers"),
        "following": user.get("following"),
        "tweets": user.get("tweets"),
        "likes": user.get("likes"),
        "media_count": user.get("media_count"),
        "description": raw.get("text") or user.get("description"),
        "location": user.get("location"),
        "joined": user.get("joined"),
    }


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    command, arg = argv[1], argv[2]
    if command == "tweet":
        user = None
        if "--user" in argv:
            idx = argv.index("--user")
            if idx + 1 < len(argv):
                user = argv[idx + 1]
        parsed_user, status_id = parse_status_ref(arg)
        screen_name = user or parsed_user
        path = f"/{screen_name}/status/{status_id}" if screen_name else f"/status/{status_id}"
        data = fetch(path)
        tweet = data.get("tweet")
        if not tweet:
            print(json.dumps({"error": "no tweet in response",
                              "api_message": data.get("message")}), file=sys.stderr)
            return 1
        print(json.dumps(summarize_tweet(tweet), ensure_ascii=False, indent=2))
        return 0
    if command == "user":
        screen_name = arg.lstrip("@")
        data = fetch(f"/{screen_name}")
        user = data.get("user")
        if not user:
            print(json.dumps({"error": "no user in response",
                              "api_message": data.get("message")}), file=sys.stderr)
            return 1
        print(json.dumps(summarize_user(user), ensure_ascii=False, indent=2))
        return 0
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
