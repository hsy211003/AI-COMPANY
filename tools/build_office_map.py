#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SY COMPANY 사무실 타일 맵 생성기 + 연결성 검증"""
from collections import deque

W, H = 35, 38
WALL, FLOOR, CORR, DOOR = '#', '.', ':', '+'
DESK, SEAT, TABLE, SOFA, ENTRY = 'D', 'o', 'T', 'S', 'E'
BLOCKING = {WALL, DESK, TABLE, SOFA}

BANDS = {'A': 1, 'B': 9, 'C': 17, 'D': 25, 'E': 33}   # 각 밴드 내부 4행
COLS = {1: 1, 2: 11, 3: 21}                            # 각 열 내부 9칸
VCORR = (31, 33)                                       # 세로 복도 x범위
CORR_ROWS = [6, 7, 14, 15, 22, 23, 30, 31]             # 가로 복도 y (2칸 폭)

# (밴드, 열, 방이름, 인원명단)  — 밴드 A~D는 문이 아래벽, E는 문이 위벽
ROOMS = [
    ('A', 1, '시장조사팀',   ['한지운(레이더)', '서민재', '오하늘']),
    ('A', 2, '브랜드 분석팀', ['정세라(나침반)', '김도윤', '배유진']),
    ('A', 3, '기획 1팀',     ['문태현(스파크)', '이나윤', '강준서']),
    ('B', 1, '검수팀',       ['백승호(필터)', '윤가온', '신예린']),
    ('B', 2, '기획 2팀',     ['조민우(펜촉)', '하시윤', '권보라']),
    ('B', 3, '영상 제작팀',   ['남기훈(필름)', '최재이', '임소정']),
    ('C', 1, '이미지 제작팀', ['유가람(팔레트)', '박선우', '고은채']),
    ('C', 2, '협업 소통팀',   ['심우재(브릿지)', '노아린']),
    ('C', 3, '정산팀',       ['차정후(장부)', '홍세연']),
    ('D', 1, '성과리뷰팀',   ['구다인(돋보기)', '양지호', '안하람']),
    ('D', 2, '자동화 운영',   ['진성재(톱니)', '도경민']),
    ('D', 3, '비서실',       ['은수현(메트로놈)', '표지우']),
    ('E', 1, '라운지',       []),
    ('E', 2, '회의실',       []),
    ('E', 3, '대표실',       ['대표']),
]

grid = [[WALL] * W for _ in range(H)]

# 1) 방 내부 바닥
for by in BANDS.values():
    for y in range(by, by + 4):
        for x in range(1, 30):
            grid[y][x] = WALL if x in (10, 20, 30) else FLOOR

# 2) 가로 복도
for y in CORR_ROWS:
    for x in range(1, 34):
        grid[y][x] = CORR

# 3) 세로 복도
for y in range(1, H - 1):
    for x in range(VCORR[0], VCORR[1] + 1):
        grid[y][x] = CORR

rooms_meta = []

def place_desks(x0, y0, names):
    """책상은 내부 첫 줄, 자리(의자)는 그 아래 줄."""
    offsets = [1, 4, 7] if len(names) == 3 else ([2, 6] if len(names) == 2 else [2])
    seats = []
    for name, dx in zip(names, offsets):
        grid[y0][x0 + dx] = DESK
        grid[y0 + 1][x0 + dx] = SEAT
        seats.append({'이름': name, '책상': [x0 + dx, y0], '자리': [x0 + dx, y0 + 1]})
    return seats

for band, col, name, members in ROOMS:
    y0, x0 = BANDS[band], COLS[col]
    seats = []
    if name == '회의실':
        for x in range(x0 + 1, x0 + 8):          # 회의 테이블 7칸
            grid[y0 + 1][x] = TABLE
            grid[y0][x] = SEAT                    # 위쪽 7석
            grid[y0 + 2][x] = SEAT                # 아래쪽 7석
            seats.append({'이름': '—', '책상': None, '자리': [x, y0]})
            seats.append({'이름': '—', '책상': None, '자리': [x, y0 + 2]})
    elif name == '라운지':
        for tx in (x0 + 2, x0 + 5):               # 라운지 테이블 2개
            grid[y0 + 1][tx] = SOFA
            grid[y0][tx] = SEAT
            grid[y0 + 2][tx] = SEAT
        grid[y0][x0] = SOFA                       # 자판기
    else:
        seats = place_desks(x0, y0, members)

    # 문: A~D는 아래벽, E는 위벽
    door = (x0 + 4, y0 + 4) if band != 'E' else (x0 + 4, y0 - 1)
    grid[door[1]][door[0]] = DOOR
    rooms_meta.append({
        '방': name, '밴드': band,
        '내부범위': {'x': [x0, x0 + 8], 'y': [y0, y0 + 3]},
        '문': list(door), '정원': len(members) if members else len(seats),
        '자리': seats,
    })

# 4) 출입구
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

desk_total = sum(1 for row in grid for c in row if c == DESK)
seat_total = sum(1 for row in grid for c in row if c == SEAT)

print('맵 크기:', W, 'x', H)
print('책상 수:', desk_total, '/ 자리(의자) 수:', seat_total)
print('도달 가능 타일:', len(seen))
print('문제:', problems if problems else '없음')
print()
for row in grid:
    print(''.join(row))

