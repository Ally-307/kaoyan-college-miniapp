#!/usr/bin/env python3
"""导入已验证的复试线/录取数据。

CSV 必须是 data/verified/reexam_lines.csv，且每条记录都必须带
source_url（来源链接）和 updated_at（数据更新时间），否则会被拒绝。
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(ROOT, "miniapp", "data", "schools.json")
DEFAULT_CSV = os.path.join(ROOT, "data", "verified", "reexam_lines.csv")
REQUIRED = ["school_name", "major_code", "year", "reexam_line", "source_url", "updated_at"]


def to_int(value):
    value = (value or "").strip()
    return int(float(value)) if value else None


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    if not os.path.exists(csv_path):
        print("找不到 CSV：", csv_path)
        sys.exit(1)

    data = json.load(open(FP, encoding="utf-8"))
    schools = {s["name"]: s for s in data["schools"]}

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("CSV 为空，未导入任何数据")
        return

    missing_cols = [c for c in REQUIRED if c not in rows[0]]
    if missing_cols:
        print("CSV 缺少必需列：", ", ".join(missing_cols))
        sys.exit(1)

    matched = 0
    skipped = []
    for r in rows:
        school_name = (r.get("school_name") or "").strip()
        major_code = (r.get("major_code") or "").strip()
        source_url = (r.get("source_url") or "").strip()
        updated_at = (r.get("updated_at") or "").strip()

        if not source_url or not updated_at:
            skipped.append(f"{school_name}|{major_code}|missing-source")
            continue

        school = schools.get(school_name)
        if not school:
            skipped.append(f"{school_name}|{major_code}|school-not-found")
            continue
        major = next((m for m in school.get("majors", []) if m["code"] == major_code), None)
        if not major:
            skipped.append(f"{school_name}|{major_code}|major-not-found")
            continue

        entry = {
            "year": int(float((r.get("year") or "").strip())),
            "reexamLine": to_int(r.get("reexam_line")),
            "reexamLineNote": (r.get("reexam_line_note") or "").strip(),
            "minAdmissionScore": to_int(r.get("min_admission_score")),
            "maxAdmissionScore": to_int(r.get("max_admission_score")),
            "avgAdmissionScore": to_int(r.get("avg_admission_score")),
            "source": source_url,
            "updatedAt": updated_at,
            "note": (r.get("note") or "").strip(),
        }
        entry = {k: v for k, v in entry.items() if v is not None and v != ""}

        admission = major.setdefault("admissionData", [])
        admission[:] = [e for e in admission if e.get("year") != entry["year"]]
        admission.append(entry)
        admission.sort(key=lambda e: e["year"], reverse=True)
        matched += 1

    # 与 final_build.py 相同的校验：没有来源或超出总分的记录不允许生成
    invalid = 0
    missing_source = 0
    for s in data["schools"]:
        for m in s.get("majors", []):
            total_score = (m.get("initialExam") or {}).get("totalScore") or 0
            for d in m.get("admissionData") or []:
                if not d.get("source") or not d.get("updatedAt"):
                    missing_source += 1
                line = d.get("reexamLine") or 0
                if total_score and line > total_score:
                    invalid += 1
    if invalid or missing_source:
        print(f"ERROR: {invalid} 条超出总分，{missing_source} 条缺少来源，拒绝写入")
        sys.exit(1)

    j = json.dumps(data, ensure_ascii=False, indent=2)
    with open(FP, "w", encoding="utf-8") as f:
        f.write(j)
    with open(FP.replace(".json", ".js"), "w", encoding="utf-8") as f:
        f.write("var schoolData = " + j + ";\nmodule.exports = schoolData;\n")

    print(f"导入完成：{matched} 条已验证数据，跳过 {len(skipped)} 条")
    for item in skipped[:20]:
        print("  跳过：", item)
    if len(skipped) > 20:
        print(f"  ... 还有 {len(skipped) - 20} 条")


if __name__ == "__main__":
    main()
