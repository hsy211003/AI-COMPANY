#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SY COMPANY 사무실 타일 맵 생성기 + 연결성 검증

인원 편성은 대표가 준 엑셀(사규 1장)을 그대로 옮긴 것이다.
직원 수·팀 구성이 바뀌면 이 파일의 ROOMS만 고치면 지도·문서·시뮬레이터가 함께 따라온다.
"""
from collections import deque

W, H = 35, 39
WALL, FLOOR, CORR, DOOR = '#', '.', ':', '+'
DESK, SEAT, TABLE, SOFA, ENTRY = 'D', 'o', 'T', 'S', 'E'
BLOCKING = {WALL, DESK, TABLE, SOFA}

BANDS = {'A': 1, 'B': 9, 'C': 17, 'D': 25, 'E': 33}   # 각 밴드 내부 시작 행
# E열(라운지·회의실)만 5행. 회의 테이블 양쪽에 통로를 둬야 먼저 앉은 사람이
# 뒷사람의 길을 막지 않는다.
BAND_H = {'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 5}
COLS = {1: 1, 2: 11, 3: 21}                            # 각 열 내부 9칸
COL_WALLS = (10, 20, 30)
VCORR = (31, 33)                                       # 세로 복도 x범위
CORR_ROWS = [6, 7, 14, 15, 22, 23, 30, 31]             # 가로 복도 y (2칸 폭)

# (밴드, 시작열, 열 개수, 방이름, [(이름, 코드명, 맡는 일, 상세)])
# 밴드 A~D는 문이 아래벽, E는 문이 위벽
ROOMS = [
    ('A', 1, 1, '시장조사팀', [
        ('한지운', '레이더', '출처 검증·최종 판단', '팀원이 서칭한 모든 내용 오류 없게 검증'),
        ('서민재', None, '뉴스 수집', 'MZ·20대 타겟 유행하는 밈 조사'),
        ('오하늘', None, '동향 조사', "한국 뷰티 브랜드 '기초 제품' 중심 타사 동향 조사"),
    ]),
    ('A', 2, 1, '브랜드 분석팀', [
        ('정세라', '나침반', '페르소나 적합성', '토리든 페르소나에 맞는지 최종 판단'),
        ('김도윤', None, '지표 분석', '계정 통계 기반 지표 분석'),
        ('배유진', None, '페르소나 검증', '기초 제품에 관심이 높은 2040 여성'),
    ]),
    ('A', 3, 1, '기획 1팀', [
        ('문태현', '스파크', '아이디어 총괄', "국내 뷰티 브랜드 '토리든'의 퍼포먼스 광고 아이디어"),
        ('이나윤', None, '기존 제품 광고 문안', '토리든 다이브인 세럼·마스크·수딩크림·선크림'),
        ('강준서', None, '신규 제품 광고 문안', '인텐시브 장벽 크림·토너·랩핑마스크'),
    ]),
    ('B', 1, 1, '검수팀', [
        ('백승호', '필터', '최종 반려 결정', '팀원이 서칭한 모든 내용 오류 없게 검증'),
        ('윤가온', None, '중복·근거 검사', '이슈가 될 만한 부분이 있는지 검사'),
        ('신예린', None, '톤 검수', '토리든 톤에 어울리는지 검사'),
    ]),
    ('B', 2, 1, '기획 2팀', [
        ('조민우', '펜촉', '아이디어 총괄', "퍼포먼스 광고 아이디어 '10-20 타겟 / 성분흡수 포지셔닝 소재'"),
        ('하시윤', None, '광고 문안', '10-20대 타겟 전용 신규 소재 발굴'),
        ('권보라', None, '광고 문안', "'성분흡수' 포지셔닝 고효율 소재 발굴"),
    ]),
    ('B', 3, 1, '네이밍팀', [
        ('유가람', '팔레트', '검증·최종 판단', '캠페인명·소재명 오류 없는지 검증'),
        ('박선우', None, '광고 소재명', '학습된 구분자로 광고 소재명 제작 (신규 엑셀 넣기 전까지 구분자 유지)'),
        ('고은채', None, '광고 캠페인명', '학습된 구분자로 광고 캠페인명 제작 (신규 엑셀 넣기 전까지 구분자 유지)'),
    ]),
    ('C', 1, 1, '협업 소통팀', [
        ('심우재', '브릿지', '협업 적합성 판단', '들어온 제안이 토리든 결에 맞는지 판단'),
        ('노아린', None, '답장 초안', '발송하지 않고 초안까지만 준비'),
    ]),
    ('C', 2, 1, '성과리뷰팀', [
        ('구다인', '돋보기', '학습점 도출', '양지호에게 전달받은 지표 확인 후 학습점 도출'),
        ('양지호', None, '지표 수집', '안하람에게 전달받은 패턴 정리 지표 수집'),
        ('안하람', None, '패턴 정리', '엑셀 파일 전달 시 패턴 수집 후 양지호에게 넘김'),
    ]),
    ('C', 3, 1, '자동화 운영', [
        ('진성재', '톱니', '연동·재시도', '끊긴 연결 재시도, 안 되는 건 안 된다고 기록'),
        ('도경민', None, '모니터링', '연동 상태 주기 확인'),
    ]),
    ('D', 1, 1, '비서실', [
        ('은수현', '메트로놈', '전사 브리핑', '병목 하나를 짚어 대표에게 보고'),
        ('표지우', None, '보고 취합', '10개 팀 보고 취합'),
    ]),
    ('D', 2, 1, '자료실', []),
    ('D', 3, 1, '대표실', [('대표', None, '결재', '하루 한 건 결정')]),
    ('E', 1, 1, '라운지', []),
    ('E', 2, 2, '회의실', []),
]

grid = [[WALL] * W for _ in range(H)]

# 1) 방 내부 바닥 + 열 사이 벽
for band, by in BANDS.items():
    for y in range(by, by + BAND_H[band]):
        for x in range(1, 30):
            grid[y][x] = WALL if x in COL_WALLS else FLOOR

# 2) 여러 열을 쓰는 방은 그 사이 벽을 튼다
for band, col, span, name, members in ROOMS:
    if span == 1:
        continue
    by = BANDS[band]
    for c in range(col, col + span - 1):
        wx = COLS[c] + 9
        for y in range(by, by + BAND_H[band]):
            grid[y][wx] = FLOOR

# 3) 가로 복도
for y in CORR_ROWS:
    for x in range(1, 34):
        grid[y][x] = CORR

# 4) 세로 복도
for y in range(1, H - 1):
    for x in range(VCORR[0], VCORR[1] + 1):
        grid[y][x] = CORR

rooms_meta = []

def place_desks(x0, y0, members):
    """책상은 내부 첫 줄, 자리(의자)는 그 아래 줄."""
    n = len(members)
    offsets = {3: [1, 4, 7], 2: [2, 6], 1: [4]}[n]
    seats = []
    for (nm, code, job, detail), dx in zip(members, offsets):
        grid[y0][x0 + dx] = DESK
        grid[y0 + 1][x0 + dx] = SEAT
        seats.append({'이름': f'{nm}({code})' if code else nm, '성명': nm, '코드명': code,
                      '맡는 일': job, '상세': detail,
                      '책상': [x0 + dx, y0], '자리': [x0 + dx, y0 + 1]})
    return seats

for band, col, span, name, members in ROOMS:
    y0 = BANDS[band]
    x0 = COLS[col]
    x1 = COLS[col + span - 1] + 8
    seats = []
    if name == '회의실':
        # y0 = 문 앞 통로, y0+1 = 위쪽 좌석, y0+2 = 테이블, y0+3 = 아래쪽 좌석, y0+4 = 통로
        ta, tb = x0 + 4, x1 - 4
        for x in range(ta, tb + 1):
            grid[y0 + 2][x] = TABLE
            grid[y0 + 1][x] = SEAT
            grid[y0 + 3][x] = SEAT
            seats.append({'이름': '—', '책상': None, '자리': [x, y0 + 1]})
            seats.append({'이름': '—', '책상': None, '자리': [x, y0 + 3]})
    elif name == '라운지':
        for tx in (x0 + 2, x0 + 5):               # 라운지 테이블 2개
            grid[y0 + 2][tx] = SOFA
            grid[y0 + 1][tx] = SEAT
            grid[y0 + 3][tx] = SEAT
        grid[y0 + 1][x0] = SOFA                   # 자판기
    elif name == '자료실':
        # 선반 두 줄 사이에 통로를 둔다. 문이 아래벽이므로 마지막 줄은 반드시 비운다.
        for x in range(x0 + 1, x0 + 8):
            grid[y0][x] = SOFA
            grid[y0 + 2][x] = SOFA
    else:
        seats = place_desks(x0, y0, members)

    door_x = (x0 + x1) // 2
    door = (door_x, y0 + BAND_H[band]) if band != 'E' else (door_x, y0 - 1)
    grid[door[1]][door[0]] = DOOR
    rooms_meta.append({
        '방': name, '밴드': band,
        '내부범위': {'x': [x0, x1], 'y': [y0, y0 + BAND_H[band] - 1]},
        '문': list(door), '정원': len(members), '자리': seats,
    })

# 5) 출입구
grid[H - 1][32] = ENTRY

# ── 검증: 출입구에서 모든 자리·바닥에 도달 가능한가 ──────────────
start = (32, H - 1)
seen = {start}
q = deque([start])
while q:
    x, y = q.popleft()
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen:
            if grid[ny][nx] not in BLOCKING:
                seen.add((nx, ny))
                q.append((nx, ny))

problems = []
for r in rooms_meta:
    if tuple(r['문']) not in seen:
        problems.append(f"{r['방']} 문 도달 불가")
    for s in r['자리']:
        if tuple(s['자리']) not in seen:
            problems.append(f"{r['방']} {s['이름']} 자리 도달 불가 {s['자리']}")
    (xa, xb), (ya, yb) = r['내부범위']['x'], r['내부범위']['y']
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            if grid[y][x] not in BLOCKING and (x, y) not in seen:
                problems.append(f"{r['방']} 내부 ({x},{y}) 고립")

# ── 회의실 좌석 검증 ──────────────────────────────────────────
# 어떤 순서로 앉든 뒷사람이 갇히지 않으려면, 나머지 좌석이 전부 차 있어도
# 문에서 각 좌석까지 길이 있어야 한다.
mr = next(r for r in rooms_meta if r['방'] == '회의실')
mr_seats = [tuple(s['자리']) for s in mr['자리']]
door = tuple(mr['문'])
for target in mr_seats:
    blocked = {s for s in mr_seats if s != target}
    seen2 = {door}
    q2 = deque([door])
    while q2:
        x, y = q2.popleft()
        for nx, ny in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in seen2: continue
            if grid[ny][nx] in BLOCKING or (nx, ny) in blocked: continue
            seen2.add((nx, ny)); q2.append((nx, ny))
    if target not in seen2:
        problems.append(f"회의실 좌석 {target} — 다른 좌석이 다 차면 도달 불가")

staff = [s for r in rooms_meta if r['방'] not in ('회의실', '라운지', '자료실', '대표실')
         for s in r['자리']]
leads = [s for s in staff if s.get('코드명')]
if len(mr_seats) < len(leads) + 1:
    problems.append(f"회의실 좌석 {len(mr_seats)}석 — 팀장 {len(leads)}명 + 대표를 못 앉힘")

desk_total = sum(1 for row in grid for c in row if c == DESK)
seat_total = sum(1 for row in grid for c in row if c == SEAT)

if __name__ == '__main__':
    print('맵 크기:', W, 'x', H)
    teams = [r for r in rooms_meta if r['방'] not in ('회의실', '라운지', '자료실', '대표실')]
    print('직원:', len(staff), '명 / 팀장:', len(leads), '명 / 팀:', len(teams))
    print('책상 수:', desk_total, '/ 자리(의자) 수:', seat_total, '/ 회의실 좌석:', len(mr_seats))
    print('도달 가능 타일:', len(seen))
    print('문제:', problems if problems else '없음')
    print()
    for row in grid:
        print(''.join(row))
