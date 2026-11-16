"""Growx Tech IT - Reddit autopost via RSS + IFTTT (free, no PC, no Reddit API key).

Run once a day by a Claude scheduled task with DAILY_MODE=true; it releases that day's posts
queue/ into docs/feed.xml. IFTTT watches that feed and submits it to Reddit.
Days vary 0-2 posts (first 14 days: 1/day), max 26/month to fit IFTTT free credits.
Delete/edit a file in queue/ to skip/change it. Create a PAUSE file to stop.
"""
import datetime as dt
import html
import json
import os
import random
import shutil
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).parent
QUEUE, POSTED = ROOT / "queue", ROOT / "posted"
STATE, FEED = ROOT / "state.json", ROOT / "docs" / "feed.xml"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
WARMUP_DAYS, FEED_SIZE = 14, 20
MONTHLY_CAP = 26  # IFTTT free = 1000 credits/month, ~35 credits per post


def parse_post(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        _, head, body = text.split("---", 2)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body.split("<!--")[0].strip()


def write_feed(items):
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>',
           "<title>Growx Reddit Feed</title><link>https://github.com/</link>",
           "<description>Queued Reddit posts</description>"]
    for it in items:
        out.append(
            "<item>"
            f"<title>{html.escape(it['title'])}</title>"
            f"<author>{html.escape(it['subreddit'])}</author>"
            f"<category>{html.escape(it['subreddit'])}</category>"
            f"<guid isPermaLink=\"false\">{it['id']}</guid>"
            f"<link>https://github.com/#{it['id']}</link>"
            f"<pubDate>{it['date']}</pubDate>"
            f"<description><![CDATA[{it['body']}]]></description>"
            "</item>")
    out.append("</channel></rss>")
    FEED.parent.mkdir(exist_ok=True)
    FEED.write_text("\n".join(out), encoding="utf-8")


def main():
    force = os.environ.get("FORCE_POST") == "true"
    if (ROOT / "PAUSE").exists() and not force:
        print("PAUSE file found - skipping.")
        return
    now = dt.datetime.now(IST)
    today = now.date().isoformat()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    state.setdefault("start_date", today)
    state.setdefault("feed", [])
    if state.get("date") != today:
        age = (now.date() - dt.date.fromisoformat(state["start_date"])).days
        month = today[:7]
        if state.get("month") != month:
            state.update(month=month, month_count=0)
        left = MONTHLY_CAP - state["month_count"]
        target = 1 if age < WARMUP_DAYS else random.choice([0, 1, 1, 1, 2])
        state.update(date=today, posted_today=0, target=max(0, min(target, left)))

    # runs every ~2h between 08:30 and 22:30 IST; GitHub may delay or skip some runs
    daily = os.environ.get("DAILY_MODE") == "true"  # one run per day: release the whole day's quota now
    need = state["target"] - state["posted_today"]
    if force:
        count = 1
    elif daily:
        count = max(0, need)
    else:
        remaining = 1 if now.hour >= 20 else max(1, (22 - now.hour) // 2)
        count = 1 if need > 0 and (need >= remaining or random.random() < need / remaining) else 0
    print(f"{today} target={state['target']} done={state['posted_today']} releasing={count}")

    for _ in range(count):
        files = sorted(QUEUE.glob("*.md"))
        if not files:
            print("Queue empty - add more posts.")
            break
        path = files[0]
        meta, body = parse_post(path)
        stamp = dt.datetime.now(IST)
        state["feed"].insert(0, {"id": f"{path.stem}-{stamp:%Y%m%d%H%M%S}",
                                 "title": meta["title"], "subreddit": meta["subreddit"],
                                 "body": html.escape(body, quote=False).replace("\n", "<br>"),
                                 "date": format_datetime(stamp)})
        state["feed"] = state["feed"][:FEED_SIZE]
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n<!-- released {stamp.isoformat()} -->\n")
        shutil.move(str(path), POSTED / path.name)
        state["posted_today"] += 1
        state["month_count"] = state.get("month_count", 0) + 1
        print("Released:", meta["title"])
    print("Queue left:", len(list(QUEUE.glob("*.md"))))

    write_feed(state["feed"])
    STATE.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
