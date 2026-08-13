#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""자료실 사이트(archive.html)를 만든다. 인원 편성은 지도 데이터에서 그대로 가져온다."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NON_TEAM = ("회의실", "라운지", "자료실", "대표실")

with open(f"{REPO}/office_map.json", encoding="utf-8") as f:
    omap = json.load(f)

teams = []
for r in omap["rooms"]:
    if r["방"] in NON_TEAM or not r["자리"]:
        continue
    teams.append({
        "team": r["방"],
        "members": [{"name": s["성명"], "code": s.get("코드명"),
                     "job": s.get("맡는 일", ""), "detail": s.get("상세", "")}
                    for s in r["자리"]],
    })

roster = {"teams": teams,
          "staff": sum(len(t["members"]) for t in teams),
          "leads": sum(1 for t in teams for m in t["members"] if m["code"])}

with open(f"{REPO}/tools/store.js", encoding="utf-8") as f:
    store_js = f.read()
with open(f"{REPO}/tools/site_template.html", encoding="utf-8") as f:
    html = f.read()

html = html.replace("/*__STORE__*/", store_js)
html = html.replace("/*__ROSTER__*/null", json.dumps(roster, ensure_ascii=False, separators=(",", ":")))

out = f"{REPO}/archive.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"archive.html 작성 완료 — {len(teams)}팀 {roster['staff']}명, {len(html)//1024}KB")
