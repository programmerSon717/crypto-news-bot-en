"""표시 문구와 탭 이름.

이 리포는 영문판 전용이다. 한국어판(crypto-news-bot)에서 갈라져 나왔고,
갈라진 이유는 한국어판을 절대 건드리지 않기 위해서다.
로직 수정은 두 리포에 각각 적용해야 한다 — 자동으로 따라가지 않는다.
"""

STRINGS = {
    "section_default": "Key points",
    "update": "Update",
    "source_link": "Read the original",
    "posted": "Published",
    "insight_context": "Context",
    "insight_impact": "Impact",
    "insight_watch": "What to watch",
    "author_original": "original post",
    "digest_title": "recap",
    "digest_count": "{n} published this hour",
    "overview_title": "briefing",
    "overview_by_cat": "By tab",
    "overview_count": "{n} in total this hour",
}


def T(key: str) -> str:
    return STRINGS[key]
