# crypto-news-bot-en 인수인계 문서

> **영문판 봇이다.** 한국어판(`programmerSon717/crypto-news-bot`)에서 갈라져 나왔고
> **코드를 공유하지 않는다.**
> 최종 갱신: 2026-09-03
>
> 전체 지형은 상위 폴더의 `START_HERE.md` 를 먼저 읽어라.
> 연결 정보(토큰·키)는 `HANDOFF.local.md` — gitignore 처리, 로컬 전용.
> 공개 상태판: **https://programmerson717.github.io/crypto-news-bot-en/**

---

## 0. 지금 상태 (2026-09-03)

| 항목 | 상태 |
|---|---|
| 텔레그램 봇 | `@CryptoNewsKingEN_bot` |
| 그룹 | Woojin-Son's Crypto Stash · 슈퍼그룹 · 포럼(탭) 켜짐 |
| 탭 | 16개 (2-1) |
| 요약 엔진 | Gemini 무료 · **한국어판과 다른 프로젝트 키** (6절) |
| 누적 발행 | 약 1,170건 |
| 클라우드 | GitHub Actions · **자체 체인 없음** ← 아래 참고 |
| 콘솔 | GitHub Pages |

### ⚠️ 지금 유일하게 급한 것 — `WORKFLOW_PAT` 이 없다

봇은 5시간 30분 루프를 돌고 끝날 때 스스로 다음 루프를 예약한다. 그 예약에 PAT 이
필요한데(기본 `GITHUB_TOKEN` 으로는 워크플로를 못 띄운다 — GitHub 이 무한 재귀
방지로 막아둠) **이 리포에는 없다.** 실제 로그:

```
⚠️ 다음 루프 예약 실패 (HTTP ...) — cron 이 대신 깨우기를 기다린다
```

cron 은 못 믿는다(한국어판 실측: 하루 6~32회, 간격 중앙값 42분, 최대 11시간 공백).
그래서 2026-09-03 에 **3시간 넘게 발행이 멈췄다.**

사용자가 만들어 줘야 한다 — fine-grained PAT, 이 리포만, **Actions: Read and write**,
만료 없음. 받으면 `WORKFLOW_PAT` 시크릿으로 등록한다.

### 손대기 전에 알아야 할 것

1. **`RULES.md` 를 먼저 읽어라.**
2. **잘 돌고 있는 것을 건드리지 마라.** 개선점이 보이면 코드를 고치지 말고 보고해 승인받아라.
3. **작업 중에 발행이 멈추면 안 된다.** 급하지 않은 변경은 푸시만 하고 다음 루프에서
   자연히 갈아타게 둔다. 실행을 함부로 취소하지 마라.
4. **한국어판에 영향이 가면 안 된다.** 리포가 갈라져 있으니 이 폴더 안에서만 작업해라.

---

## 0-1. 한국어판과 무엇이 같고 무엇이 다른가

**같은 것 (한쪽을 고치면 반대편도 고쳐야 한다)**

```
main.py  country.py  summarizer.py  store.py  publisher.py  digest.py
prefilter.py  urgent.py  collectors/*  admin/*  워크플로 구조
```

발행 로직·수집기·요약기는 언어와 무관하다. 실측상 로직 커밋이 하루 4건꼴이었고,
한쪽만 고치면 두 판이 조용히 달라진다.

**다른 것**

| | 한국어판 | 영문판(이 리포) |
|---|---|---|
| 프롬프트 | `prompts_ko.py` | `prompts.py` |
| 분류 키 | `이슈` `거래소이슈` `국내정책` `해외정책` `US Rates` | `Main Issue` `Exchange Issue` `Korea Policy` `Global Policy` `US Macro` |
| 탭 이름 | 🚨주요이슈 · 🏦거래소이슈 | 🚨Main Issue · 🏦Exchange Issue |
| 시각 표기 | `🕒 2026-08-30 07:00 KST 게시` | `🕒 Posted 2026-08-30 7:17 PM EDT` |
| 하단 문구 | `기사 원문 - 매체명` | `Original Article - Outlet` |
| region_hint | `미국/규제` `지표:` `긴급:` | `US/regulation` `indicator:` `urgent:` |
| 소스 이름 | `블록미디어` `빗썸 공지` | `Blockmedia` `Bithumb Notice` |

**분류 키를 번역하지 마라.** 라우팅·중복판정·렌더링이 그 문자열로 돈다.
독자에게는 `topics.CATEGORIES` 의 표시 이름만 보인다.

**이미 갈라진 것 하나:** 이 리포에는 `summarizer.MODEL_RPM` 표가 있고 한국어판에는 없다.
분당 한도가 계열마다 다른데(Flash Lite 15, 풀 Flash 5) 양쪽 다 12 를 쓰고 있었다.
과거분 이관 속도 때문에 여기만 먼저 고쳤다(건당 30초 → 8건/분).

---

## 1. 발행 포맷

```
📕 US tax authority publishes crypto capital gains figures for the first time

☑️ HMRC has introduced a dedicated crypto category in its capital gains tax statistics…

📁 Key tax figures
┃ • 17,600 individuals reported 13.8 billion pounds in crypto disposal proceeds…
┃ • 240 high-income filers reported gains of 1 million pounds or more…

🐧 This gives us a rare, hard look at actual tax compliance…

🔁 Update            ← 이미 나간 글과 겹치지만 새 내용이 있을 때만

🕒 Posted 2026-08-30 6:55 PM EDT

Original Article - TokenPost

#GlobalPolicy #Regulation #Tax #UK
```

**헤드라인·소제목은 문장형(sentence case)** 이다. 로이터·블룸버그 방식으로 첫 낱말과
고유명사만 대문자로 쓴다. 티커·약어는 자기 표기를 유지한다(BTC, SEC, HMRC, KOSPI).

**시각은 미 동부시간 12시간제**다. `ZoneInfo("America/New_York")` 를 써서 서머타임이
자동으로 갈린다(EDT ↔ EST). 한국어판은 KST 지만 이 채널 독자에게 한국 시간은 기준이
못 되고, 크립토 시장의 기준 시계는 뉴욕이다.

---

## 2. 탭 (2-1)

| 분류 키 | 탭 이름 | thread | 해시태그 |
|---|---|---|---|
| `Korea Policy` | 🇰🇷Korea Policy | 2 | #KoreaPolicy |
| `US Policy` | 🇺🇸US Policy | 3 | #USPolicy |
| `Japan Policy` | 🇯🇵Japan Policy | 4 | #JapanPolicy |
| `Hong Kong Policy` | 🇭🇰Hong Kong Policy | 5 | #HongKongPolicy |
| `Singapore Policy` | 🇸🇬Singapore Policy | 6 | #SingaporePolicy |
| `UAE Policy` | 🇦🇪UAE Policy | 7 | #UAEPolicy |
| `Vietnam Policy` | 🇻🇳Vietnam Policy | 8 | #VietnamPolicy |
| `Global Policy` | 🌎Global Policy | 9 | #GlobalPolicy |
| `Korea Macro` | 🇰🇷Korea Macro | 10 | #KoreaMacro |
| `US Macro` | 🇺🇸US Macro | 11 | #USMacro |
| `Korea Equities` | 🇰🇷Korea Equities | 12 | #KoreaEquities |
| `US Equities` | 🇺🇸US Equities | 13 | #USEquities |
| `China` | 🇨🇳China Policy | 14 | #ChinaPolicy |
| `Global Macro` | 🌐Global Macro | 15 | #GlobalMacro |
| `Exchange Issue` | 🏦Exchange Issue | 16 | #ExchangeIssue |
| `Main Issue` | 🚨Main Issue | 17 | #MainIssue |

해시태그의 첫 태그는 **코드가 탭 이름에서 자동 생성**한다(`publisher._tab_tag`).
모델에 맡기면 탭과 다른 값을 뱉는다.

---

## 3. 발행 범위 — 중요도가 아니라 주제로 가른다

이 채널이 다루는 것은 **크립토·토큰화·블록체인**이고, 그게 글의 **주어**여야 한다.

```
발행    주어가 크립토인 것 — 제3자 수치, 온체인 사실, 자산의 보안·기술 논쟁,
        기관의 크립토 사업 결정. 중요도 3이면 충분하다.

제외    주어가 예측 시장(Polymarket·Kalshi·ParlayX)이거나 AI(에이전트 경제·
        기업 실적·지출)인 것. 체인 위에서 돈다는 이유만으로는 주제가 아니다.
```

**도구로 등장하는 것은 버리지 않는다.** 주어가 무엇인지로 가른다.

```
AI 챗봇 링크로 지갑이 털렸다        → 주어는 자산 탈취    → 발행
양자컴퓨터가 비트코인 서명을 깨나    → 주어는 BTC 보안    → 발행
AI 에이전트가 수익을 홀더와 나눈다   → 주어는 AI 사업모델  → 제외
예측시장에 기관 자금이 들어온다      → 주어는 예측시장    → 제외
```

한때 이슈 탭 문턱을 4로 올린 적이 있는데, 홍보성 글은 막혔지만 **토큰화 주식 거래량·
온체인 대규모 출금·시총 비교 같은 진짜 시장 뉴스도 3점으로 채점돼 같이 잘렸다**
(실측: 유효 20건 중 발행 가능 1건). 문턱은 홍보글과 시장 뉴스를 구분하지 못한다.
지금 문턱은 **3**(정책 탭도 3, 거래소이슈는 면제)이다.

---

## 4. 실행 방법

```bash
cd ~/Desktop/HanwhaDAPnews/crypto-news-bot-en

venv/bin/python main.py --once --dry-run    # 진단은 항상 dry-run
venv/bin/python main.py --once              # 전체 스윕 1회
venv/bin/python main.py --urgent            # 긴급 레인
venv/bin/python main.py --digest            # 다이제스트
venv/bin/python admin/snapshot.py --write   # 상태판 갱신
venv/bin/python tools/overview_count.py     # 총괄 브리핑 발행 횟수(커밋 신원 판정용)
```

> **로컬에서 발행 모드를 돌리지 마라.** 클라우드와 동시에 켜지면 같은 뉴스가 두 번
> 발행된다. 과거분 이관 때는 클라우드 워크플로를 꺼두고 로컬로만 돌렸다.

---

## 5. 과거분 이관 도구 (`tools/`)

한국어판이 발행한 글을 영문으로 옮겨 이 채널에 다시 올린 도구다. 2026-08-30 에
**381건을 실패 0으로** 옮겼다. 다시 쓸 일은 없겠지만 구조를 남겨 둔다.

```
tools/parse_published.py   발행문(HTML)을 부품으로 역파싱. 381건 전부 성공
tools/backfill_ko.py       오래된 것부터 번역·발행. 중단돼도 이어서 한다
ko_seed.sqlite3            한국어판 발행 이력 사본. 이관 원재료
```

원 기사를 다시 긁지 않고 **이미 만들어 둔 결과물**을 재료로 썼다 — 옛 URL 은 상당수
죽었고, 사실관계는 이미 검증돼 있으며, 요약을 두 번 하지 않아 한도를 아낀다.
그래서 '재요약'이 아니라 '옮기기'다. bullet 개수·수치·인명이 보존된다.

만들며 밟은 함정:
- 사진이 딸린 글은 제목이 캡션에 있어 본문에 제목 줄이 없다. 아래 `🗣 <b>… 원문</b>`
  줄을 제목으로 오인해 이모지가 🗣 로 붙었다.
- 원문 글자 잔존 검사에서 **괄호 안은 빼야 한다.** 고유명사 병기는 정상이다
  (`牛来USDT` → `Niulai (牛来) USDT`). 안 그러면 정상 번역이 버려진다.

---

## 6. 무료 한도

**한국어판과 다른 Google Cloud 프로젝트 키를 쓴다.** 프로젝트 번호 `911987766800`.
한도가 프로젝트 단위라 통이 분리된다 — 실증도 했다(영문 키를 분당 한도까지 밀어붙인
그 순간 한국어 키는 정상 동작).

```
Flash Lite 계열   분당 15   (설정 12)
풀 Flash 계열     분당  5   (설정 4)   ← MODEL_RPM 표
gemini-3.1-flash-lite  일일 500
풀 Flash 계열          일일  20
```

리셋은 태평양 자정 = **16:00 KST**. 한도에 걸린 모델은 `MODEL_COOLDOWN_SEC`(15분)
만큼 쉬고 다시 시도한다 — **영구 배제하면 안 된다.**

---

## 7. 배포·운영

푸시하면 새 실행이 대기열에 서고, 도는 루프가 끝나면 이어받는다.
**급하지 않으면 취소하지 마라** — 취소하면 그 사이 공백이 생긴다.

즉시 갈아타야 할 때만 실행을 취소한다(`START_HERE.md` 6절의 상태 확인 명령 참고).

**"멈춘 것 같다" 진단 순서**

```
① 폴링이 도는가        git log origin/main | grep '발행 이력'   (5~20분 간격이면 정상)
② 마지막 발행이 언제인가  git show origin/main:botstate.sqlite3
③ 모델 한도가 남았는가   7개 중 몇 개가 살아 있는지 직접 찔러본다
④ 처리할 뉴스가 있는가   main.py --once --dry-run
```

- **커밋은 나는데 발행이 0인 상태가 정상일 수 있다.** 상태판 파일이 폴링마다 바뀐다.
- **새벽에는 발행 0건이 정상이다.** 미국 장이 닫히고 아시아가 안 열린 시간대다.
- **`cancelled` 는 실패가 아니다.** 루프가 도는 동안 들어온 예약이 밀려난 것이다.

---

## 8. 함정

1. **`run:` 블록 안에서 heredoc 을 쓰면 YAML 이 깨진다.** 본문이 열 0 에서 시작하기
   때문이다. 실제로 두 번 깨뜨렸다. 파이썬이 필요하면 `tools/` 에 파일로 빼라.
2. **커밋 메시지에 건너뛰기 표시(대괄호 skip ci)를 '언급'만 해도 푸시가 무시된다.**
3. **분류 키를 번역하지 마라.** 라우팅이 전부 어긋난다.
4. **한도 걸린 모델을 영구 배제하지 마라.** 새벽 한 번의 오류로 아침 내내 멈춘다.
5. **로컬과 클라우드를 동시에 켜지 마라.** 같은 뉴스가 두 번 발행된다.
6. **`ast.parse` 만으로 검증하지 마라.** 문법이 맞아도 함수가 엉뚱한 자리에 들어갈 수
   있다. 반드시 `import` 까지 확인하고 푸시할 것.
7. 매체명이 원문 언어로 들어오는 경우가 있다(`… - 뉴스핌`). `publisher.OUTLETS` 에
   매핑이 있고, 없는 것은 그대로 둔다 — 없는 이름을 지어내는 것보다 낫다.

---

## 9. 되돌리기 · 잔디

**9-1. 버전 되돌리기** — 상태판의 ⏪ 버튼이나 목록의 `적용` 을 누르면
`.github/workflows/rollback.yml` 이 그 버전으로 배포한다.

되돌리는 것은 **봇 로직뿐**이다. `botstate.sqlite3`(되돌리면 이미 발행한 뉴스를 다시
뿌린다) · `topics.json`(탭이 중복 생성된다) · `docs/`·`admin/`(되돌리기 버튼 자체가
사라진다) · 문서 · `rollback.yml` 자신은 보존한다.

토큰은 리포에 없다. 브라우저 `localStorage` 에만 둔다(🔑 버튼). fine-grained PAT,
이 리포만, Actions: Read and write.

**9-2. 잔디(기여 그래프)** — 총괄 브리핑이 나간 회차만 사람 이름으로 커밋한다.

```
브리핑 회차   programmerSon717 <73008892+programmerSon717@users.noreply.github.com>
그 외 폴링    github-actions[bot]
```

판정은 `digest_log` 의 `overview` 행 수 비교(`tools/overview_count.py`).
상태판의 잔디 패널은 아이소메트릭 블록으로 그리고, 데이터는 브라우저가 외부 API 에서
직접 받아온다 — **봇 코드와 접점이 없다.**
