#!/usr/bin/env python3
"""
主数据集成器：将 522所学校 + 国家线 + 自划线高校数据整合为统一可查询数据集

输出:
  data/score_lines/schools_with_scores.json - 每所学校关联的分数线数据
  data/score_lines/school_scores_lookup.json - 按学科门类->学校的快速查找表
"""
import json
import os
import sys
from datetime import datetime, timezone

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCORE_DIR = os.path.join(BASE_DIR, "data", "score_lines")
SCHOOLS_PATH = os.path.join(BASE_DIR, "miniapp", "data", "schools.json")
NATIONAL_LINES_PATH = os.path.join(SCORE_DIR, "national_lines.json")
SELF_LINES_PATH = os.path.join(SCORE_DIR, "self_determined_lines.json")

# 学科门类代码映射 (用于匹配学校专业到国家线)
DISCIPLINE_TO_NATIONAL_LINE = {
    "哲学": "哲学",
    "经济学": "经济学",
    "法学": "法学",
    "教育学": "教育学",
    "文学": "文学",
    "历史学": "历史学",
    "理学": "理学",
    "工学": "工学",
    "农学": "农学",
    "医学": "医学",
    "军事学": "军事学",
    "管理学": "管理学",
    "艺术学": "艺术学",
    "交叉学科": "交叉学科",
}

# 自划线高校名单
SELF_DETERMINED_SCHOOLS = {
    "北京大学", "中国人民大学", "清华大学", "北京航空航天大学",
    "北京理工大学", "中国农业大学", "北京师范大学", "南开大学",
    "天津大学", "大连理工大学", "东北大学", "吉林大学",
    "哈尔滨工业大学", "复旦大学", "同济大学", "上海交通大学",
    "南京大学", "东南大学", "浙江大学", "中国科学技术大学",
    "厦门大学", "山东大学", "武汉大学", "华中科技大学",
    "湖南大学", "中南大学", "中山大学", "华南理工大学",
    "四川大学", "重庆大学", "电子科技大学", "西安交通大学",
    "西北工业大学", "兰州大学",
}


def load_schools():
    with open(SCHOOLS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("schools", [])


def load_national_lines():
    if not os.path.exists(NATIONAL_LINES_PATH):
        return {}
    with open(NATIONAL_LINES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_self_lines():
    if not os.path.exists(SELF_LINES_PATH):
        return {}
    with open(SELF_LINES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def map_school_to_score_lines(school, national_data, self_data):
    """将一所学校映射到其相关的分数线数据"""
    name = school.get("name", "")
    province = school.get("province", "")
    school_type = school.get("type", [])
    is_985 = "985" in school_type
    is_211 = "211" in school_type
    is_self = name in SELF_DETERMINED_SCHOOLS

    # 确定A/B区
    b_qu_provinces = {"内蒙古", "广西", "海南", "贵州", "云南", "西藏", "甘肃", "青海", "宁夏", "新疆"}
    zone = "B" if province in b_qu_provinces else "A"
    zone_label = "B区" if zone == "B" else "A区"

    result = {
        "schoolId": school.get("id", ""),
        "name": name,
        "province": province,
        "region": school.get("region", ""),
        "type": school_type,
        "zone": zone,
        "zoneLabel": zone_label,
        "isSelfDetermined": is_self,
        "scoreInfo": {},
    }

    # 1. 国家线数据（所有学校都适用）
    unified_lines = national_data.get("unified_lines", [])
    separate_lines = national_data.get("separate_lines", [])

    # 为每个学科门类映射国家线
    result["scoreInfo"]["nationalLines"] = {}
    for item in unified_lines:
        discipline = item.get("name", "")
        gjx = item.get("gjx", {})
        type_scores = gjx.get("typea" if zone == "A" else "typeb", [])

        # 获取2026年总分
        latest_total = type_scores[-1] if type_scores else None

        result["scoreInfo"]["nationalLines"][discipline] = {
            "totalScores": {
                "2022": type_scores[0] if len(type_scores) > 0 else None,
                "2023": type_scores[1] if len(type_scores) > 1 else None,
                "2024": type_scores[2] if len(type_scores) > 2 else None,
                "2025": type_scores[3] if len(type_scores) > 3 else None,
                "2026": type_scores[4] if len(type_scores) > 4 else None,
            },
            "singleSubjectScores": {},
        }

        # 添加单科分数线
        for dk in item.get("dkx", []):
            year = dk.get("year", "")
            if year:
                result["scoreInfo"]["nationalLines"][discipline]["singleSubjectScores"][year] = {
                    "subject1": dk.get("typeaone" if zone == "A" else "typebone", ""),
                    "subject2": dk.get("typeatwo" if zone == "A" else "typebtwo", ""),
                }

    # 专业学位国家线
    result["scoreInfo"]["professionalLines"] = {}
    for item in separate_lines:
        name = item.get("name", "")
        gjx = item.get("gjx", {})
        type_scores = gjx.get("typea" if zone == "A" else "typeb", [])
        result["scoreInfo"]["professionalLines"][name] = {
            "totalScores": {
                "2022": type_scores[0] if len(type_scores) > 0 else None,
                "2023": type_scores[1] if len(type_scores) > 1 else None,
                "2024": type_scores[2] if len(type_scores) > 2 else None,
                "2025": type_scores[3] if len(type_scores) > 3 else None,
                "2026": type_scores[4] if len(type_scores) > 4 else None,
            },
        }

    # 2. 自划线高校特定数据
    if is_self:
        self_result = None
        schools_list = self_data.get("schools", [])
        for s in schools_list:
            if s.get("yxmc") == name:
                self_result = s
                break

        if self_result:
            result["scoreInfo"]["selfDeterminedUrls"] = {}
            for y in self_result.get("yearList", []):
                result["scoreInfo"]["selfDeterminedUrls"][y["year"]] = y["url"]

    result["scoreInfo"]["note"] = (
        "自划线高校复试基本线高于国家线" if is_self
        else "执行国家线，各专业复试线由学校在国家线基础上自定"
    )

    return result


def build_discipline_lookup(schools_with_scores):
    """构建按学科门类查找学校的索引"""
    lookup = {}

    for school in schools_with_scores:
        name = school["name"]
        zone = school["zone"]
        zone_label = school["zoneLabel"]
        school_type = school["type"]

        for discipline, line_data in school.get("scoreInfo", {}).get("nationalLines", {}).items():
            if discipline not in lookup:
                lookup[discipline] = {"A区": [], "B区": []}

            latest = line_data.get("totalScores", {}).get("2026")
            lookup[discipline][zone_label].append({
                "name": name,
                "type": school_type,
                "province": school["province"],
                "isSelfDetermined": school.get("isSelfDetermined", False),
                "nationalLine2026": latest,
            })

    # 按分数线排序
    for discipline in lookup:
        for zone_key in lookup[discipline]:
            lookup[discipline][zone_key].sort(
                key=lambda x: x.get("nationalLine2026") or 0, reverse=True
            )

    return lookup


def print_summary(schools_with_scores, lookup):
    """打印数据摘要"""
    total = len(schools_with_scores)
    self_count = sum(1 for s in schools_with_scores if s["isSelfDetermined"])
    a_count = sum(1 for s in schools_with_scores if s["zone"] == "A")
    b_count = sum(1 for s in schools_with_scores if s["zone"] == "B")

    print(f"  学校总数: {total}")
    print(f"  自划线高校: {self_count}")
    print(f"  A区学校: {a_count}")
    print(f"  B区学校: {b_count}")
    print(f"  学科门类索引: {len(lookup)} 个门类")

    print(f"\n  各学科 2026年A区国家线及关联学校数:")
    for discipline in sorted(lookup.keys()):
        a_schools = len(lookup[discipline].get("A区", []))
        b_schools = len(lookup[discipline].get("B区", []))

        # 找到这个学科的2026年A区国家线
        sample_line = None
        for s in lookup[discipline]["A区"][:1]:
            sample_line = s.get("nationalLine2026")
            break

        print(f"    {discipline}: {sample_line}分, A区{a_schools}所 + B区{b_schools}所")


def main():
    print("考研复试分数线主数据集成器")
    print("=" * 60)
    print()

    # 加载数据
    print("加载数据...")
    schools = load_schools()
    national_data = load_national_lines()
    self_data = load_self_lines()
    print(f"  学校: {len(schools)} 所")
    print(f"  国家线: {'已加载' if national_data else '未找到'}")
    print(f"  自划线: {'已加载' if self_data else '未找到'}")
    print()

    # 整合
    print("整合数据...")
    schools_with_scores = []
    for school in schools:
        enriched = map_school_to_score_lines(school, national_data, self_data)
        schools_with_scores.append(enriched)

    # 构建查找索引
    print("构建学科索引...")
    lookup = build_discipline_lookup(schools_with_scores)

    # 保存
    print("保存文件...")
    result = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "description": "考研院校复试分数线集成数据集",
        "dataSources": {
            "schools": SCHOOLS_PATH,
            "nationalLines": NATIONAL_LINES_PATH,
            "selfDeterminedLines": SELF_LINES_PATH,
        },
        "summary": {
            "totalSchools": len(schools_with_scores),
            "selfDeterminedSchools": sum(1 for s in schools_with_scores if s["isSelfDetermined"]),
            "aZoneSchools": sum(1 for s in schools_with_scores if s["zone"] == "A"),
            "bZoneSchools": sum(1 for s in schools_with_scores if s["zone"] == "B"),
            "disciplinesCovered": len(lookup),
            "yearsCovered": ["2022", "2023", "2024", "2025", "2026"],
        },
        "schools": schools_with_scores,
        "disciplineLookup": {d: lookup[d] for d in sorted(lookup.keys())},
    }

    out_path = os.path.join(SCORE_DIR, "schools_with_scores.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(out_path)
    print(f"  ✓ {out_path} ({file_size / 1024 / 1024:.1f} MB)")

    # 简化版查找表（用于小程序快速查询）
    lookup_simple = {}
    for discipline in sorted(lookup.keys()):
        lookup_simple[discipline] = {
            "A区": [],
            "B区": [],
        }
        for zone_key in ["A区", "B区"]:
            for school in lookup[discipline][zone_key]:
                lookup_simple[discipline][zone_key].append({
                    "name": school["name"],
                    "type": school["type"],
                    "line2026": school.get("nationalLine2026"),
                })

    lookup_path = os.path.join(SCORE_DIR, "school_scores_lookup.json")
    with open(lookup_path, "w", encoding="utf-8") as f:
        json.dump({
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "disciplines": lookup_simple,
        }, f, ensure_ascii=False, indent=2)

    size2 = os.path.getsize(lookup_path)
    print(f"  ✓ {lookup_path} ({size2 / 1024:.1f} KB)")

    # 打印摘要
    print()
    print_summary(schools_with_scores, lookup)

    print()
    print("=" * 60)
    print("集成完成！")


if __name__ == "__main__":
    main()
