#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bearzo1_YT site auto-updater
============================
Scrapes youtube.com/@bearzo1_yt, picks the current TOP 6 videos by view count,
and rewrites the VIDEOS=[...] array in every copy of the site.

- Views are shown "friendly" (floored + a plus): 1.5K+, 1K+, 500+, 300+ ...
- Dates are shortened: "3 yr ago", "5 mo ago", "3 wk ago".
- Deleted videos vanish automatically (they simply won't be in the live top 6).
- SAFE: if the scrape returns nothing, it aborts and leaves every file untouched.

Run manually:      python3 update_videos.py
Preview only:      python3 update_videos.py --dry-run

Only uses the Python standard library (no pip installs).
"""
import re, sys, json, os, time, urllib.request, datetime

CHANNEL = "https://www.youtube.com/@bearzo1_yt/videos"
TOP_N   = 6

# Every copy of the site that should be kept in sync. Missing paths are skipped.
TARGETS = [
    "/Users/bgaurav/Downloads/Frost Storage/Claude Projects/bearzo.club/index.html",
    "/Users/bgaurav/Desktop/bearzo-github/index.html",
    "/Users/bgaurav/Desktop/bearzo1-yt.html",
    "/tmp/bearzo/index.html",
]

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_videos.log")


def log(msg):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def fetch(url, tries=3):
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def parse_views(raw):
    """'1.8K' -> 1800, '531' -> 531, '2.3M' -> 2300000, '1,234' -> 1234."""
    raw = raw.strip().replace(",", "")
    m = re.match(r"^([\d.]+)\s*([KM]?)$", raw)
    if not m:
        return None
    n = float(m.group(1))
    unit = m.group(2)
    if unit == "K":
        n *= 1_000
    elif unit == "M":
        n *= 1_000_000
    return int(round(n))


def friendly(n):
    """Floor to a clean number and add '+'. 1800->'1.5K+', 1000->'1K+', 531->'500+'."""
    if n >= 1_000_000:
        base = (n // 100_000) * 100_000
        v = base / 1_000_000
        return (f"{v:.1f}".rstrip("0").rstrip(".")) + "M+"
    if n >= 1_000:
        base = (n // 500) * 500          # floor to nearest 500
        if base % 1_000 == 0:
            return f"{base // 1000}K+"
        return f"{base / 1000:.1f}K+"     # e.g. 1500 -> '1.5K+'
    if n >= 100:
        return f"{(n // 100) * 100}+"
    if n >= 10:
        return f"{(n // 10) * 10}+"
    return f"{n}"


def short_date(txt):
    """'3 years ago' -> '3 yr ago', '5 months ago' -> '5 mo ago', etc."""
    if not txt:
        return ""
    m = re.match(r"(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago", txt)
    if not m:
        return txt
    n, unit = m.group(1), m.group(2)
    abbr = {"second": "sec", "minute": "min", "hour": "hr",
            "day": "days", "week": "wk", "month": "mo", "year": "yr"}[unit]
    return f"{n} {abbr} ago"


def unescape(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return (s.replace('\\"', '"').replace("\\/", "/").replace("\\\\", "\\"))


def scrape(html):
    ids, seen = [], set()
    for m in re.finditer(r'"videoId":"([\w-]{11})"', html):
        vid = m.group(1)
        if vid not in seen:
            seen.add(vid)
            ids.append((vid, m.start()))
    out = []
    for vid, pos in ids:
        win = html[pos:pos + 6000]
        tm = re.search(r'"lockupMetadataViewModel":\{"title":\{"content":"((?:[^"\\]|\\.)*)"', win)
        if not tm:
            tm = re.search(r'"content":"((?:[^"\\]|\\.)*)"', win)
        title = unescape(tm.group(1)) if tm else None
        vm = re.search(r'"([\d.,]+[KM]?) views"', win)
        views = parse_views(vm.group(1)) if vm else None
        dm = re.search(r'(\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago)', win)
        date = short_date(dm.group(1)) if dm else ""
        if title and views is not None:
            out.append({"id": vid, "title": title, "views": views, "date": date})
    out.sort(key=lambda v: v["views"], reverse=True)
    return out


def build_array(vids):
    lines = ["const VIDEOS=["]
    for i, v in enumerate(vids):
        obj = (f'{{id:{json.dumps(v["id"])},'
               f'title:{json.dumps(v["title"], ensure_ascii=False)},'
               f'views:{json.dumps(friendly(v["views"]))},'
               f'date:{json.dumps(v["date"])}}}')
        lines.append("  " + obj + ("," if i < len(vids) - 1 else ""))
    lines.append("]")
    return "\n".join(lines)


def split_friendly(fr):
    """'1.5K+' -> ('1.5','K+');  '500+' -> ('500','+')."""
    m = re.match(r"^([\d.]+)(.*)$", fr)
    return (m.group(1), m.group(2)) if m else (fr, "")


def set_stat(html, stat, count, suffix):
    """Patch a hero stat tile marked data-stat="<stat>" (keeps stats honest)."""
    pat = re.compile(r'(data-count=")[^"]*("\s+data-suffix=")[^"]*("\s+data-stat="' + re.escape(stat) + r'")')
    return pat.sub(lambda m: m.group(1) + count + m.group(2) + suffix + m.group(3), html, count=1)


def main():
    dry = "--dry-run" in sys.argv
    log("=== update starting ===")
    try:
        html = fetch(CHANNEL)
    except Exception as e:
        log(f"ABORT: could not fetch channel ({e}). Files left untouched.")
        return 1

    vids = scrape(html)
    if len(vids) < 1:
        log("ABORT: parsed 0 videos (YouTube layout may have changed). Files left untouched.")
        return 1

    top = vids[:TOP_N]
    log(f"parsed {len(vids)} videos; top {len(top)}:")
    for i, v in enumerate(top):
        log(f"  #{i+1} {friendly(v['views']):>6} views · {v['date']:<10} {v['title'][:60]} ({v['id']})")

    new_arr = build_array(top)
    pat = re.compile(r"const VIDEOS=\[.*?\]", re.DOTALL)

    # hero stat tiles kept in sync with reality
    vid_count = str(len(vids))
    top_num, top_suf = split_friendly(friendly(top[0]["views"]))
    log(f"stats -> videos:{vid_count}+  top video:{top_num}{top_suf}")

    if dry:
        log("--dry-run: not writing. New array would be:\n" + new_arr)
        return 0

    changed = 0
    for path in TARGETS:
        if not os.path.exists(path):
            log(f"skip (missing): {path}")
            continue
        s = open(path, encoding="utf-8").read()
        if not pat.search(s):
            log(f"skip (no VIDEOS array found): {path}")
            continue
        s2 = pat.sub(lambda _m: new_arr, s, count=1)
        s2 = set_stat(s2, "videos", vid_count, "+")
        s2 = set_stat(s2, "topviews", top_num, top_suf)
        if s2 != s:
            open(path, "w", encoding="utf-8").write(s2)
            changed += 1
            log(f"updated: {path}")
        else:
            log(f"no change: {path}")

    log(f"=== done: {changed} file(s) updated ===")
    log("NOTE: re-upload index.html from ~/Desktop/bearzo-github/ to GitHub Pages to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
