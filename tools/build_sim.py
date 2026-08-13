#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""office_map.json + 말버릇 → 단일 HTML 시뮬레이터(office_sim.html)로 합친다."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 사규(AI_COMPANY_PRO.md) 1장의 말버릇 2줄
LINES = {
    "한지운(레이더)":   ["출처 두 개 이상 안 나오면 안 씁니다.", "이건 작년 기사예요, 걸러냅니다."],
    "서민재":           ["요즘 20대가 쓰는 밈만 걷어왔어요.", "유행 지난 건 따로 빼둘게요."],
    "오하늘":           ["타사 기초 라인 3주째 같은 흐름이에요.", "이건 반짝이 아니라 추세입니다."],
    "정세라(나침반)":   ["우리 채널 결이랑 안 맞아요.", "숫자 없으면 판단 안 합니다."],
    "김도윤":           ["지표가 안 들어와서 계산을 못 해요.", "증가율은 확인된 것만 말씀드릴게요."],
    "배유진":           ["2040 여성이 쓸 말투가 아니에요.", "이 표현, 대표님이라면 안 쓰실 것 같아요."],
    "문태현(스파크)":   ["일단 열 개 깔고 시작하죠.", "재미없으면 제가 먼저 버립니다."],
    "이나윤":           ["다이브인 세럼은 이미 많이 나갔어요.", "기존 제품은 새 각도로 다시 씁니다."],
    "강준서":           ["장벽 크림은 아직 아무도 안 다뤘어요.", "신제품은 첫 3초에서 승부 봅니다."],
    "백승호(필터)":     ["근거 링크 없는 안은 반려예요.", "금칙어 스캔 돌립니다."],
    "윤가온":           ["지난달에 나간 것과 겹칩니다.", "이슈 될 만한 표현이 하나 있어요."],
    "신예린":           ["토리든 톤에서 벗어났어요.", "표현만 다듬으면 통과입니다."],
    "조민우(펜촉)":     ["10-20 타겟은 호흡이 달라야죠.", "길면 자릅니다, 미련 없이."],
    "하시윤":           ["10대가 쓰는 말로 다시 썼어요.", "이 문장은 입에 안 붙어요."],
    "권보라":           ["성분흡수 쪽으로 각을 잡았습니다.", "고효율 소재부터 올릴게요."],
    "유가람(팔레트)":   ["구분자 안 맞는 이름은 반려합니다.", "캠페인명부터 검증할게요."],
    "박선우":           ["소재명은 구분자 규칙대로 뽑습니다.", "새 엑셀 오기 전까진 이 규칙 유지예요."],
    "고은채":           ["캠페인명 후보 뽑아뒀어요.", "구분자 파일이 있어야 시작합니다."],
    "심우재(브릿지)":   ["이 제안, 우리 결에 안 맞아요.", "조건부터 확인하고 답합니다."],
    "노아린":           ["초안만 써뒀어요, 발송은 안 했습니다.", "거절 문구도 같이 준비했어요."],
    "구다인(돋보기)":   ["잘된 이유를 못 찾으면 성공 아닙니다.", "다음에 써먹을 한 줄만 남기죠."],
    "양지호":           ["통계가 안 붙어서 수치는 비워뒀어요.", "안하람한테 받은 것만 올립니다."],
    "안하람":           ["엑셀 주시면 패턴부터 뽑을게요.", "같은 패턴이 세 번째예요."],
    "진성재(톱니)":     ["연결이 끊겨서 재시도 걸어뒀습니다.", "안 되는 건 안 된다고 적습니다."],
    "도경민":           ["지금 두 곳이 응답 없어요.", "10분 간격으로 보고 있습니다."],
    "은수현(메트로놈)": ["지금 병목은 하나입니다.", "결재만 주시면 바로 넘어갑니다."],
    "표지우":           ["10개 팀 보고 다 걷었어요.", "빠진 팀은 사유까지 받아뒀습니다."],
}

with open(f"{REPO}/office_map.json", encoding="utf-8") as f:
    omap = json.load(f)

NON_TEAM = ("회의실", "라운지", "자료실", "대표실")
placed = [s["이름"] for r in omap["rooms"] if r["방"] not in NON_TEAM for s in r["자리"]]
missing = [n for n in placed if n not in LINES]
extra = [n for n in LINES if n not in placed]
assert not missing and not extra, f"명단 불일치 — 지도에만: {missing} / 말버릇에만: {extra}"

with open(f"{REPO}/tools/store.js", encoding="utf-8") as f:
    store_js = f.read()
with open(f"{REPO}/tools/sim_template.html", encoding="utf-8") as f:
    html = f.read()

html = html.replace("/*__STORE__*/", store_js)

html = html.replace("/*__MAP__*/null", json.dumps(omap, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*__LINES__*/null", json.dumps(LINES, ensure_ascii=False, separators=(",", ":")))

out = f"{REPO}/office_sim.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"office_sim.html 작성 완료 — 직원 {len(placed)}명 배치, {len(html)//1024}KB")
