#!/usr/bin/env python3
"""Steam price watch: check watched games against the public Steam store API.

Reads games.json next to this script: a list of
  {"appid": int, "name": str, "target_price_yen": int|null, "min_discount_percent": int}

Prints one line per game that meets its criteria (discount >= min_discount_percent,
or final price <= target_price_yen when set). Prints nothing when nothing matches.
Prices are JPY (cc=jp). No API key needed. Never buys anything.
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def fetch(appid: int) -> dict | None:
    url = (
        f"https://store.steampowered.com/api/appdetails?appids={appid}"
        "&cc=jp&l=japanese&filters=price_overview"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    entry = data.get(str(appid)) or {}
    if not entry.get("success"):
        return None
    return (entry.get("data") or {}).get("price_overview")


def main() -> int:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "games.json"
    games = json.loads(config_path.read_text(encoding="utf-8"))
    for g in games:
        try:
            p = fetch(int(g["appid"]))
        except Exception as e:  # network hiccup: report on stderr, keep going
            print(f"WARN {g.get('name')}: {e}", file=sys.stderr)
            continue
        if not p:
            continue  # free-to-play or no price data
        final = p["final"] / 100
        initial = p["initial"] / 100
        discount = int(p.get("discount_percent") or 0)
        target = g.get("target_price_yen")
        min_disc = int(g.get("min_discount_percent", 20))
        hit = discount >= min_disc or (target is not None and final <= target)
        if hit:
            print(
                f"{g['name']}: ¥{final:,.0f}（定価 ¥{initial:,.0f}、{discount}%オフ） "
                f"https://store.steampowered.com/app/{g['appid']}/"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
