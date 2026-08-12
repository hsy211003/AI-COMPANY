#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""검증된 맵 데이터를 OFFICE_MAP.md / office_map.json 으로 출력"""
import json, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_office_map as m   # 생성 + 검증 실행

grid, rooms, W, H = m.grid, m.rooms_meta, m.W, m.H
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── ASCII 맵 (좌표 눈금 포함) ──────────────────────────────
tens = '    ' + ''.join(str(x // 10) if x % 10 == 0 else ' ' for x in range(W))
ones = '    ' + ''.join(str(x % 10) for x in range(W))
lines = [tens, ones]
for y, row in enumerate(grid):
    lines.append(f'{y:>2}  ' + ''.join(row))
ascii_map = '\n'.join(lines)

BAND_LABEL = {'A': '1층 A열', 'B': '1층 B열', 'C': '1층 C열', 'D': '1층 D열', 'E': '1층 E열'}

# ── 방 표 ────────────────────────────────────────────────
room_rows = []
for r in rooms:
    xa, xb = r['내부범위']['x']; ya, yb = r['내부범위']['y']
    seats = len(r['자리']) if r['방'] != '라운지' else 4
    room_rows.append(
        f"| {r['방']} | {r['밴드']}열 | ({xa},{ya})–({xb},{yb}) | ({r['문'][0]},{r['문'][1]}) | {seats} |")

# ── 자리 배정 표 ──────────────────────────────────────────
seat_rows = []
for r in rooms:
    if r['방'] in ('회의실', '라운지'):
        continue
    for s in r['자리']:
        d = f"({s['책상'][0]},{s['책상'][1]})"
        c = f"({s['자리'][0]},{s['자리'][1]})"
        seat_rows.append(f"| {s['이름']} | {r['방']} | {d} | {c} |")

meeting = [s['자리'] for r in rooms if r['방'] == '회의실' for s in r['자리']]
meeting_txt = ', '.join(f"({x},{y})" for x, y in meeting)

doc = f"""# SY COMPANY — 사무실 지도

> 이 문서는 `AI_COMPANY.md` · `AI_COMPANY_PRO.md`를 전제로 한다.
> 직원 32명 + 대표 1명이 실제로 **이 좌표 위에서 움직인다.**
> 좌표는 `(x, y)` — x는 왼쪽부터 0, y는 위쪽부터 0.

---

## 1. 타일 지도 ({W} × {H})

```
{ascii_map}
```

## 2. 타일 기호

| 기호 | 뜻 | 통과 |
|---|---|---|
| `#` | 벽 | ❌ 막힘 |
| `D` | 책상 | ❌ 막힘 |
| `T` | 회의 테이블 | ❌ 막힘 |
| `S` | 라운지 테이블·자판기 | ❌ 막힘 |
| `+` | 문 | ✅ 통과 |
| `o` | 자리(의자) — 직원이 서는 칸 | ✅ 통과 |
| `.` | 방 바닥 | ✅ 통과 |
| `:` | 복도 | ✅ 통과 |
| `E` | 출입구 | ✅ 통과 |

**이동 규칙**
```
① 상하좌우 4방향으로만 움직인다 (대각선 금지)
② `#` `D` `T` `S` 칸은 절대 지나갈 수 없다
③ 방을 드나들 때는 반드시 그 방의 문(`+`)을 지난다 — 벽을 뚫지 않는다
④ 책상(`D`)에는 올라서지 않는다. 직원은 책상 바로 아래 자리(`o`)에 선다
⑤ 두 직원이 같은 칸에 동시에 설 수 없다 (복도에서 마주치면 한 명이 비켜선다)
```

## 3. 방 배치

가로 복도 4개(y=6·13·20·27)와 오른쪽 세로 복도(x=31~33)가 모든 방을 잇는다.
출입구 `(32, 33)`에서 세로 복도로 들어와 각 층 복도로 갈라진다.

| 방 | 위치 | 내부 범위 | 문 | 자리 수 |
|---|---|---|---|---|
{chr(10).join(room_rows)}

## 4. 자리 배정 (33석)

| 이름 | 방 | 책상 | 자리 |
|---|---|---|---|
{chr(10).join(seat_rows)}

**회의실 좌석 14석** (테이블 위·아래 각 7석)
```
{meeting_txt}
```
팀장 12명 + 대표 1명이 앉고도 1석이 남는다.

**라운지** — 배정석 없음. 테이블 2개와 의자 4석, 자판기 1대.

## 5. 사규와의 연결

```
① 07:00 출근  → 전원 출입구(32,33)에서 시작해 각자 자리(o)로 이동
② 인수인계 회의 → 해당 부서 인원만 회의실로 이동, 좌석에 앉는다
③ "회의 소집"  → 팀장 12명이 자기 방 문을 나와 회의실 좌석으로 이동
④ ⑦ 승인 대기  → 담당자들은 회의실 좌석에 앉은 채로 대기한다 (자리로 안 돌아감)
⑤ 자율 행동    → 라운지(1열 E)로만 이동 가능. 다른 부서 방에는 들어가지 않는다
⑥ "집중 모드"  → 라운지·복도에 있는 전원이 자기 자리(o)로 복귀
⑦ 브리핑      → 비서실장 은수현이 비서실(D열 3) → 복도 → 대표실 문(25,28)로 이동
```

**비서실장 브리핑 동선** (은수현: 자리 (23,23) → 대표실)
```
(23,23) → (23,25) 아래로 → (25,25) → 문(25,26) → 복도 y=27 → 문(25,28) → 대표실
```
비서실이 대표실 바로 위에 있어 최단 동선이다.
"""

with open(f'{REPO}/OFFICE_MAP.md', 'w', encoding='utf-8') as f:
    f.write(doc)

payload = {
    'name': 'SY COMPANY OFFICE',
    'width': W, 'height': H,
    'legend': {
        '#': {'name': '벽', 'blocking': True},
        'D': {'name': '책상', 'blocking': True},
        'T': {'name': '회의 테이블', 'blocking': True},
        'S': {'name': '라운지 가구', 'blocking': True},
        '+': {'name': '문', 'blocking': False},
        'o': {'name': '자리', 'blocking': False},
        '.': {'name': '방 바닥', 'blocking': False},
        ':': {'name': '복도', 'blocking': False},
        'E': {'name': '출입구', 'blocking': False},
    },
    'entrance': [32, H - 1],
    'corridors': {'horizontal_y': m.CORR_ROWS, 'vertical_x': [31, 33]},
    'tiles': [''.join(r) for r in grid],
    'rooms': rooms,
}
with open(f'{REPO}/office_map.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print('OFFICE_MAP.md / office_map.json 작성 완료')
