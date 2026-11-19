#!/usr/bin/env python3
"""Steam discovery: find highly rated games currently on sale.

Reads Steam search results (specials only, sorted by review score, JPY).
Each result row carries the discount, final price, and the review summary
(descriptor, positive %, review count), so no per-game calls are needed.
Filters:
  - discount >= 30%
  - positive review ratio >= 90% with at least 1,000 reviews
Sorted by review ratio, then review count. Skips games already reported
in the last 21 days (state in reported.json next to this script), unless
their discount has deepened since. Prints at most 8 lines.
"""
import html as html_mod
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "reported.json"
MAX_LINES = 8
SKIP_DAYS = 21

ROW_RE = re.compile(r'<a [^>]*data-ds-appid="(\d+)"[^>]*>(.*?)</a>\s*(?=<a |$)', re.S)
TITLE_RE = re.compile(r'<span class="title">([^<]+)</span>')
DISCOUNT_RE = re.compile(r'data-discount="(\d+)"')
FINAL_RE = re.compile(r'data-price-final="(\d+)"')
TOOLTIP_RE = re.compile(r'data-tooltip-html="([^"]+)"')
REVIEW_RE = re.compile(r'([\d,]+)件中(\d+)%')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    games: dict[int, dict] = {}
    for start in (0, 100):
        try:
            data = json.loads(
                fetch(
                    "https://store.steampowered.com/search/results/?query"
                    f"&start={start}&count=100&dynamic_data=&sort_by=Reviews_DESC"
                    "&specials=1&infinite=1&cc=jp&l=japanese"
                )
            )
        except Exception:
            continue
        for appid_s, row in ROW_RE.findall(data.get("results_html") or ""):
            appid = int(appid_s)
            if appid in games:
                continue
            tip_m = TOOLTIP_RE.search(row)
            disc_m = DISCOUNT_RE.search(row)
            fin_m = FINAL_RE.search(row)
            name_m = TITLE_RE.search(row)
            if not (tip_m and disc_m and fin_m and name_m):
                continue
            tip = html_mod.unescape(tip_m.group(1))
            rev_m = REVIEW_RE.search(tip)
            if not rev_m:
                continue
            discount = int(disc_m.group(1))
            ratio = int(rev_m.group(2))
            total = int(rev_m.group(1).replace(",", ""))
            if discount < 30 or ratio < 90 or total < 1000:
                continue
            final = int(fin_m.group(1)) / 100  # attribute is in 1/100 yen units
            initial = round(final / (1 - discount / 100)) if discount < 100 else final
            games[appid] = {
                "appid": appid,
                "name": html_mod.unescape(name_m.group(1)),
                "discount": discount,
                "final": final,
                "initial": initial,
                "ratio": ratio,
                "total": total,
                "desc": tip.split("<br>")[0],
            }

    state = load_state()
    now = time.time()
    results = []
    for g in games.values():
        seen = state.get(str(g["appid"]))
        if seen and now - seen.get("ts", 0) < SKIP_DAYS * 86400:
            if g["discount"] <= int(seen.get("discount", 0)):
                continue
        results.append(g)

    results.sort(key=lambda r: (r["ratio"], r["total"]), reverse=True)
    for r in results[:MAX_LINES]:
        print(
            f"{r['name']}: ¥{r['final']:,.0f}（定価 ¥{r['initial']:,}、{r['discount']}%オフ） "
            f"評価: {r['desc']}（好評率{r['ratio']}%・レビュー{r['total']:,}件） "
            f"https://store.steampowered.com/app/{r['appid']}/"
        )
        state[str(r["appid"])] = {"ts": now, "discount": r["discount"]}
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
