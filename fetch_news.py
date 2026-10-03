#!/usr/bin/env python3
"""Radar de noticias tech: lee feeds RSS/Atom, deduplica y guarda docs/news.json."""
import calendar
import hashlib
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / "feeds.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / "news.json"
UA = "Mozilla/5.0 (compatible; TechRadar/1.0; personal news aggregator)"

TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str, limit: int = 280) -> str:
    text = html.unescape(TAG_RE.sub(" ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def entry_date(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)
    return datetime.now(timezone.utc)


def load_previous() -> dict:
    if OUT.exists():
        try:
            data = json.loads(OUT.read_text(encoding="utf-8"))
            return {item["id"]: item for item in data.get("items", [])}
        except (json.JSONDecodeError, KeyError):
            pass
    return {}


def main() -> int:
    items = load_previous()
    cutoff = datetime.now(timezone.utc) - timedelta(days=CONFIG["max_age_days"])
    status = []

    for feed in CONFIG["feeds"]:
        try:
            parsed = feedparser.parse(feed["url"], agent=UA)
            entries = parsed.entries[: CONFIG["max_items_per_feed"]]
            if not entries:
                raise ValueError(parsed.get("bozo_exception") or "sin entradas")
        except Exception as exc:  # un feed caído no debe romper el resto
            status.append({"source": feed["name"], "ok": False, "error": str(exc)[:120]})
            print(f"[FALLO] {feed['name']}: {exc}", file=sys.stderr)
            continue

        added = 0
        for entry in entries:
            link = entry.get("link")
            if not link:
                continue
            item_id = hashlib.sha1(link.encode()).hexdigest()[:16]
            if item_id in items:
                continue
            items[item_id] = {
                "id": item_id,
                "title": clean(entry.get("title", ""), 200),
                "url": link,
                "summary": clean(entry.get("summary", "")),
                "source": feed["name"],
                "category": feed["category"],
                "published": entry_date(entry).isoformat(),
            }
            added += 1
        status.append({"source": feed["name"], "ok": True, "new": added})
        print(f"[OK] {feed['name']}: +{added}")

    fresh = [i for i in items.values() if datetime.fromisoformat(i["published"]) >= cutoff]
    fresh.sort(key=lambda i: i["published"], reverse=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {"updated": datetime.now(timezone.utc).isoformat(), "status": status, "items": fresh},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"Total guardado: {len(fresh)} noticias")
    return 0


if __name__ == "__main__":
    sys.exit(main())
