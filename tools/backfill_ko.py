"""한국어판이 발행한 글을 영문으로 옮겨 이 채널에 다시 올린다.

원 기사를 다시 긁지 않고 **이미 만들어 둔 결과물**을 재료로 쓴다.
  · 옛 URL 은 상당수 죽거나 유료화돼 다시 못 읽는다
  · 이미 사람이 확인한 내용이라 사실관계가 검증돼 있다
  · 요약을 두 번 하지 않으니 무료 한도를 아낀다
그래서 이건 '재요약'이 아니라 '옮기기'다. bullet 개수·수치·인명이 보존된다.

    venv/bin/python tools/backfill_ko.py --dry-run --limit 3
    venv/bin/python tools/backfill_ko.py                # 실제 이관
    venv/bin/python tools/backfill_ko.py --limit 50     # 나눠서

**오래된 것부터 올린다.** 채널 규칙상 최신 글이 맨 아래여야 한다.
중단돼도 이미 옮긴 것은 published 에 남아 다시 올리지 않는다.
"""
import argparse
import asyncio
import html
import os
import re
import sqlite3
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import country                      # noqa: E402
import main as pipeline             # noqa: E402
import publisher                    # noqa: E402
import topics                       # noqa: E402
from config import settings         # noqa: E402
from prompts import TRANSLATE_SYSTEM_PROMPT, build_translate_prompt  # noqa: E402
from store import Store             # noqa: E402
from summarizer import generate_json  # noqa: E402
from tools.parse_published import parse, missing  # noqa: E402

SEED = os.path.join(ROOT, "ko_seed.sqlite3")
ET = ZoneInfo("America/New_York")
CJK = re.compile(r"[가-힣ぁ-ヿ㐀-䶵一-鿿]")

# 한국어판 분류 키 → 이 리포의 키. 이관 대상이 옛 표기를 쓰고 있다.
KEYMAP = {
    "국내정책": "Korea Policy", "해외정책": "Global Policy",
    "거래소이슈": "Exchange Issue", "이슈": "Main Issue",
    "US Rates": "US Macro", "Korea Rates": "Korea Macro",
}


def rows_to_move():
    con = sqlite3.connect(SEED)
    out = []
    for key, cat, head, url, ts, text in con.execute(
            "SELECT key, category, headline, source_url, published_at, text "
            "FROM published WHERE text IS NOT NULL AND text != '' "
            "ORDER BY COALESCE(origin_at, published_at)"):     # 오래된 것부터
        out.append({"key": key, "category": KEYMAP.get(cat, cat) or "Main Issue",
                    "headline": head, "url": url or "", "ts": ts, "text": text})
    return out


async def translate(parts: dict) -> dict | None:
    return await generate_json(TRANSLATE_SYSTEM_PROMPT, build_translate_prompt(parts))


async def prepare(r: dict) -> dict | None:
    """한 건을 번역해 발행 직전 상태까지 만든다. 발행은 하지 않는다."""
    parts = parse(r["text"])
    if not parts or missing(parts):
        return {"_skip": f"부품 부족: {r['headline'][:40]}"}
    parts["headline"] = r["headline"] or parts.get("headline", "")

    en = await translate(parts)
    if not en or not en.get("headline"):
        return {"_fail": f"번역: {r['headline'][:40]}"}

    body = " ".join(str(en.get(k, "")) for k in ("headline", "lede", "comment")) \
        + " ".join(en.get("bullets", []))
    # 괄호 안의 원어 병기는 정상이다(Niulai (牛来)). 괄호를 지우고 검사한다.
    if CJK.search(re.sub(r"\([^)]*\)", "", body)):
        return {"_fail": f"원문 글자 잔존: {r['headline'][:40]}"}

    en["header_emoji"] = parts.get("header_emoji", "📰")
    cat = pipeline.normalize_category(r["category"])
    cat, _ = country.enforce(cat, en)
    en["category"] = cat
    en["_source_name"] = parts.get("_outlet") or None
    if r["ts"]:
        dt = datetime.fromtimestamp(r["ts"], ET)
        en["_posted_label"] = (f"{dt:%Y-%m-%d} {dt:%I:%M %p}".replace(" 0", " ")
                               + f" {dt:%Z}")
    en["_row"] = r
    en["_text"] = publisher.render(en, r["url"])
    return en


async def run(limit: int | None, dry: bool, sleep: float, workers: int):
    """번역은 병렬로, 발행은 순서대로.

    번역을 순차로 돌리면 모델 대기 시간이 그대로 쌓여 건당 30초가 걸렸다.
    발행은 반드시 순서를 지켜야 한다 — 채널 규칙상 오래된 글이 위에 와야 한다.
    """
    store = Store(settings.db_path)
    rows = [r for r in rows_to_move() if not store.is_seen(r["key"])]
    print(f"[이관] 남은 것 {len(rows)}건" + (f" · 이번에 {limit}건" if limit else "")
          + f" · 번역 동시 {workers}")
    if limit:
        rows = rows[:limit]

    ok = skipped = failed = 0
    t0 = time.monotonic()
    import httpx
    async with httpx.AsyncClient() as client:
        # 순서를 지키기 위해 묶음 단위로 번역해 두고, 묶음 안에서 차례로 발행한다.
        for start in range(0, len(rows), workers):
            batch = rows[start:start + workers]
            done = await asyncio.gather(*[prepare(r) for r in batch])
            for en in done:
                if en is None or en.get("_skip"):
                    print(f"  [건너뜀] {en['_skip'] if en else ''}"); skipped += 1; continue
                if en.get("_fail"):
                    print(f"  [실패] {en['_fail']}"); failed += 1; continue
                r, text, cat = en["_row"], en["_text"], en["category"]
                if dry:
                    print(f"\n{'='*62}\n[{cat}]\n{'='*62}")
                    print(html.unescape(re.sub(r'<[^>]+>', '', text)))
                    ok += 1
                    continue
                mid = await publisher.send_raw(client, text, topics.thread_id_for(cat))
                if not mid:
                    print(f"  [실패] 발행: {en['headline'][:40]}"); failed += 1; continue
                store.mark_seen(r["key"], "ko-backfill", en["headline"])
                if r["url"]:
                    store.mark_url_seen(r["url"], "ko-backfill", en["headline"])
                store.record_published(r["key"], mid, topics.thread_id_for(cat), r["url"],
                                       en["headline"], category=cat, lede=en.get("lede", ""),
                                       text=text, origin_at=r["ts"])
                ok += 1
                if ok % 10 == 0 or ok == 1:
                    rate = ok / max(1e-9, (time.monotonic() - t0) / 60)
                    left = (len(rows) - ok) / max(rate, 1e-9)
                    print(f"  [{ok}/{len(rows)}] {rate:.1f}건/분 · 남은 시간 약 {left:.0f}분"
                          f"  {cat:<16} {en['headline'][:40]}")
                await asyncio.sleep(sleep)

    print(f"\n[이관] 완료 — 옮김 {ok} · 건너뜀 {skipped} · 실패 {failed}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=5,
                    help="동시에 번역할 건수")
    ap.add_argument("--sleep", type=float, default=3.0,
                    help="발행 간격(초). 텔레그램 그룹 제한이 분당 20건이다")
    a = ap.parse_args()
    asyncio.run(run(a.limit, a.dry_run, a.sleep, a.workers))
