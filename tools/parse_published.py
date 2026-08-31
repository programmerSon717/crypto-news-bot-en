"""발행된 글(HTML)을 다시 부품으로 뜯는다.

영문판을 만들 때 한국어판이 지금까지 발행한 글을 그대로 옮기려면, 원 기사를
다시 긁어오는 대신 **이미 만들어 둔 결과물**을 재료로 쓰는 편이 낫다.
  · 옛 URL 은 상당수가 죽거나 유료화돼 다시 못 읽는다
  · 이미 사람이 확인한 내용이라 사실관계가 검증돼 있다
  · 요약을 두 번 하지 않으니 무료 한도를 아낀다

렌더 포맷(publisher.render)이 규칙적이라 역으로 뜯을 수 있다.
"""
import html as _html
import re

_TAG = re.compile(r"<[^>]+>")


def _plain(s: str) -> str:
    return _html.unescape(_TAG.sub("", s)).strip()


def parse(text: str) -> dict | None:
    """발행 원문 → {headline, header_emoji, lede, section_title, bullets,
    comment, update_note, context, impact, watch, hashtags}"""
    if not text:
        return None
    out: dict = {"bullets": [], "hashtags": []}

    # 제목 줄은 "{이모지} <b>제목</b>" 이다. 다만 본문에는 같은 모양의 줄이 더 있다
    #   🗣 <b>… 원문</b>  📁 <b>소제목</b>  📌 <b>배경</b>  🔁 <b>업데이트</b>
    # 사진이 딸린 글은 제목이 캡션에 있어 제목 줄 자체가 없다. 그때 아래 줄을
    # 제목으로 오인하면 이모지가 🗣 로 붙는다(실제로 그랬다).
    _NOT_TITLE = ("🗣", "📁", "📌", "📈", "🔍", "🔁", "🕒", "📎")
    for m in re.finditer(r"^(\S+)\s*<b>(.*?)</b>", text, re.M):
        if m.group(1) in _NOT_TITLE:
            continue
        out["header_emoji"], out["headline"] = m.group(1), _plain(m.group(2))
        break

    m = re.search(r"^☑️\s*(.+?)$", text, re.M)
    if m:
        out["lede"] = _plain(m.group(1))

    m = re.search(r"^📁\s*<b>(.*?)</b>\s*\n<blockquote>(.*?)</blockquote>", text, re.M | re.S)
    if m:
        out["section_title"] = _plain(m.group(1))
        out["bullets"] = [_plain(b) for b in m.group(2).split("\n") if _plain(b).strip("• ")]
        out["bullets"] = [b.removeprefix("•").strip() for b in out["bullets"]]

    for emoji, key in (("📌", "context"), ("📈", "impact"), ("🔍", "watch")):
        m = re.search(rf"^{emoji}\s*<b>.*?</b>\s*\n(.+?)$", text, re.M)
        if m:
            out[key] = _plain(m.group(1))

    m = re.search(r"^🐧\s*(.+?)$", text, re.M)
    if m:
        out["comment"] = _plain(m.group(1))

    m = re.search(r"^🔁\s*<b>.*?</b>\s*\n(.+?)$", text, re.M)
    if m:
        out["update_note"] = _plain(m.group(1))

    # 원 게시물 인용(트위터 캡처 경로)
    for i, m in enumerate(re.finditer(r"<blockquote expandable>(.*?)</blockquote>", text, re.S)):
        out["origin_text" if i == 0 else "origin_text_ko"] = _plain(m.group(1))

    m = re.search(r"^🕒\s*(.+?)\s*게시\s*$", text, re.M)
    if m:
        out["_posted_label"] = m.group(1).strip()

    m = re.search(r"^(#\S.*)$", text, re.M)
    if m:
        out["hashtags"] = [t.lstrip("#") for t in _plain(m.group(1)).split()]

    # 출처 매체명. 형식이 둘이다.
    #   일반 기사   기사 원문</a> - 토큰포스트
    #   퍼온 글     📎 출처: <a href="...">Optimism Governance</a>
    m = re.search(r"기사 원문</a>\s*-\s*([^\n<]+)", text)
    if m:
        out["_outlet"] = _plain(m.group(1))
    else:
        m = re.search(r"📎\s*출처:\s*<a[^>]*>(.*?)</a>", text, re.S)
        if m:
            out["_outlet"] = _plain(m.group(1))

    return out


def missing(d: dict) -> list[str]:
    """필수 부품 중 빠진 것.

    headline 은 여기서 안 본다. 사진이 딸린 글은 제목이 캡션에 들어가 본문에
    없기 때문이다(publisher 의 _headline_in_caption 경로). 이관 도구가 DB 의
    headline 칼럼을 쓰므로 문제되지 않는다.
    """
    need = ("lede", "comment")
    out = [k for k in need if not d.get(k)]
    if not d.get("bullets"):
        out.append("bullets")
    return out
