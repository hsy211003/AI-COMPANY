#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사규(AI_COMPANY_PRO.md)의 인원 편성·말버릇·연동 대기 절을 지도 데이터에서 다시 쓴다.
편성이 바뀌어도 사규와 지도가 어긋나지 않게 하기 위한 것이다."""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{REPO}/tools")
from build_sim import LINES                      # 말버릇 원본

NON_TEAM = ("회의실", "라운지", "자료실", "대표실")

with open(f"{REPO}/office_map.json", encoding="utf-8") as f:
    omap = json.load(f)

teams = [r for r in omap["rooms"] if r["방"] not in NON_TEAM and r["자리"]]
staff = [s for r in teams for s in r["자리"]]
leads = [s for s in staff if s.get("코드명")]

# ── 1장: 인원 편성 표 ───────────────────────────────────────────
rows = []
for i, r in enumerate(teams, 1):
    for j, s in enumerate(r["자리"]):
        dept = f"[ {r['방']} ]" if j == 0 else ""
        idx = str(i) if j == 0 else ""
        rank = "실장" if (j == 0 and r["방"] == "비서실") else ("팀장" if j == 0 else "팀원")
        code = s.get("코드명") or "—"
        rows.append(f"| {idx} | {dept} | {rank} | {s['성명']} | {code} | {s['맡는 일']} | {s['상세']} |")

table = ("| # | 부서 | 직책 | 이름 | 코드명 | 맡는 일 | 맡는 일 상세 |\n"
         "|---|---|---|---|---|---|---|\n" + "\n".join(rows))

width = max(len(n) for n in LINES)
habit = "\n".join(
    f"{n}{' ' * (width - len(n))}  \"{v[0]}\" / \"{v[1]}\"" for n, v in LINES.items())

section1 = f"""## 1. 인원 편성

**총원**: 팀장 {len(leads)}명 + 팀원 {len(staff) - len(leads)}명 = **{len(staff)}명** + 대표 1명
**부서**: {len(teams)}개

{table}

**말버릇** (1인 2줄 · 이게 캐릭터를 만든다)

```
{habit}
```
"""

# ── 2장: 현재 연동 대기 항목 ────────────────────────────────────
section_link = """**현재 연동 대기 항목**
```
계정 통계 — 미연동. 브랜드 분석팀 '지표 분석'(김도윤), 성과리뷰팀 '지표 수집'(양지호) 정지
메일     — 미연동. 협업 소통팀 협업 메일 확인 정지 (심우재·노아린)
구분자 엑셀 — 미제공. 네이밍팀 '광고 소재명'(박선우), '광고 캠페인명'(고은채) 정지
패턴 엑셀  — 미제공. 성과리뷰팀 '패턴 정리'(안하람) 정지
```

이 네 가지는 모두 **대표가 자료를 주면 즉시 풀린다.** 자료실 사이트의 팀별 투입구에
파일을 넣으면 해당 담당자의 상태가 '연동 대기'에서 풀리고 그 자리에서 작업을 시작한다.

**연동 대기가 아닌 것**
```
앞 부서 결과를 기다리는 것은 전부 '대기'다. 두 상태를 절대 섞지 않는다.
```
"""

path = f"{REPO}/AI_COMPANY_PRO.md"
doc = open(path, encoding="utf-8").read()

doc = re.sub(r"## 1\. 인원 편성.*?(?=\n---)", section1, doc, flags=re.S)
doc = re.sub(r"\*\*현재 연동 대기 항목\*\*.*?(?=\n---)", section_link, doc, flags=re.S)

open(path, "w", encoding="utf-8").write(doc)
print(f"AI_COMPANY_PRO.md 갱신 — {len(teams)}팀 {len(staff)}명 (팀장 {len(leads)})")
