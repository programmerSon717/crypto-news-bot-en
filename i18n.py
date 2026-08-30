"""표시 문구와 탭 이름.

이 리포는 영문판 전용이다. 한국어판(crypto-news-bot)에서 갈라져 나왔고,
갈라진 이유는 한국어판을 절대 건드리지 않기 위해서다.
로직 수정은 두 리포에 각각 적용해야 한다 — 자동으로 따라가지 않는다.
"""

# 탭 표시 이름. 키(왼쪽)는 모델이 분류값으로 뱉는 문자열이라 **바꾸면 안 된다.**
# 한국어 키가 섞여 있는 것은 한국어판과 같은 분류 체계를 쓰기 때문이다.
# 독자에게는 오른쪽 이름만 보인다.
TAB_NAMES = {
    "국내정책": "🇰🇷Korea Policy",
    "US Policy": "🇺🇸US Policy",
    "Japan Policy": "🇯🇵Japan Policy",
    "Hong Kong Policy": "🇭🇰Hong Kong Policy",
    "Singapore Policy": "🇸🇬Singapore Policy",
    "UAE Policy": "🇦🇪UAE Policy",
    "Vietnam Policy": "🇻🇳Vietnam Policy",
    "해외정책": "🌎Global Policy",
    "China": "🇨🇳China Policy",
    "Korea Rates": "🇰🇷Korea Macro",
    "US Rates": "🇺🇸US Macro",
    "Global Macro": "🌐Global Macro",
    "Korea Equities": "🇰🇷Korea Equities",
    "US Equities": "🇺🇸US Equities",
    "거래소이슈": "🏦Exchange Watch",
    "이슈": "🚨Top Stories",
}

STRINGS = {
    "section_default": "Key points",
    "update": "Update",
    "source_link": "Read the original",
    "posted": "published",
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


def tab_names() -> dict:
    return TAB_NAMES
