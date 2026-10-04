#!/usr/bin/env python3
"""把研招网采集结果合并进 schools.json，替换掉合成专业。"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw_zsml_programs.json")
FP = os.path.join(ROOT, "miniapp", "data", "schools.json")


def to_major(school_id, program, record):
    code = program.get("zydm") or ""
    xwlx = program.get("xwlx") or ""
    return {
        "id": f"{school_id}_{code}_{xwlx}",
        "name": program.get("zymc") or "",
        "code": code,
        "category": program.get("mlmc") or "",
        "degreeType": program.get("xwlxmc") or ("专业学位" if xwlx in ("zy", "zyxw") else "学术学位"),
        "studyMode": "",
        "initialExam": {"subjects": [], "totalScore": 0},
        "reexam": {"subjects": [], "ratio": "", "method": ""},
        "admissionData": [],
        "duration": "",
        "tuition": "",
        "source": record.get("sourceUrl", ""),
        "sourceUpdatedAt": record.get("fetchedAt", ""),
        "sourceNote": "研招网硕士专业目录",
    }


def main():
    if not os.path.exists(RAW):
        print("没有采集数据，先运行：python server/collect_zsml.py --scope 985")
        return

    records = json.load(open(RAW, encoding="utf-8"))
    data = json.load(open(FP, encoding="utf-8"))
    schools_by_id = {s["id"]: s for s in data["schools"]}

    collected = set()
    total_majors = 0
    for record in records:
        school = schools_by_id.get(record["schoolId"])
        if not school:
            continue
        majors = []
        seen = set()
        for program in record.get("programs", []):
            key = (program.get("zydm"), program.get("xwlx"))
            if key in seen:
                continue
            seen.add(key)
            majors.append(to_major(school["id"], program, record))
        school["majors"] = majors
        collected.add(school["id"])
        total_majors += len(majors)
        print(f"{school['name']}: {len(majors)} 个真实专业")

    # 未采集的学校不保留合成专业，避免展示假数据
    for school in data["schools"]:
        if school["id"] not in collected:
            school["majors"] = []

    j = json.dumps(data, ensure_ascii=False, indent=2)
    with open(FP, "w", encoding="utf-8") as f:
        f.write(j)
    with open(FP.replace(".json", ".js"), "w", encoding="utf-8") as f:
        f.write("var schoolData = " + j + ";\nmodule.exports = schoolData;\n")

    print(f"完成：{len(collected)} 所学校，{total_majors} 个真实专业")


if __name__ == "__main__":
    main()
