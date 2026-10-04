import json
data = {"schools": []}

# School 1: 清华大学
tsinghua = {
    "id": "10001", "name": "清华大学", "province": "北京", "city": "北京",
    "region": "华北", "type": ["985", "211", "双一流"],
    "intro": "清华大学是中国著名高等学府，坐落于北京西北郊风景秀丽的清华园。是中国高层次人才培养和科学技术研究的重要基地之一，被誉为\u300c红色工程师的摇篮\u300d。",
    "tags": ["顶尖985", "C9"], "majors": []
}

jisuanji = {
    "id": "10001_081200", "name": "计算机科学与技术", "code": "081200",
    "category": "工学", "level1Subject": "计算机科学与技术",
    "degreeType": "学术学位", "studyMode": "全日制",
    "initialExam": {
        "subjects": [
            {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
            {"code": "201", "name": "英语（一）", "type": "统考", "score": 100, "order": 2},
            {"code": "301", "name": "数学（一）", "type": "统考", "score": 150, "order": 3},
            {"code": "912", "name": "计算机专业基础综合", "type": "自命题", "score": 150, "order": 4}
        ], "totalScore": 500
    },
    "reexam": {"subjects": ["编译原理", "计算机系统结构", "操作系统", "编程能力综合考核"], "ratio": "1.5:1", "method": "笔试+面试+上机"},
    "admissionData": [
        {"year": 2026, "reexamLine": 375, "minAdmissionScore": 385, "maxAdmissionScore": 435, "reexamCount": 30, "admissionCount": 20, "applicationCount": 580},
        {"year": 2025, "reexamLine": 365, "minAdmissionScore": 378, "maxAdmissionScore": 428, "reexamCount": 28, "admissionCount": 18, "applicationCount": 550}
    ],
    "duration": "3年", "tuition": "8000元/年", "crossMajorPolicy": "接受跨考",
    "equivalentEducationPolicy": "不接受同等学力报考", "accommodation": "提供住宿，2-4人间",
    "tags": ["顶尖", "竞争激烈"]
}
tsinghua["majors"].append(jisuanji)
data["schools"].append(tsinghua)

# Simple validation
j = json.dumps(data, ensure_ascii=False, indent=2)
json.loads(j)  # verify valid
fp = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json"
with open(fp, "w", encoding="utf-8") as f:
    f.write(j)
print("Generated schools.json with 1 school (Tsinghua)")
print("Total file size:", len(j), "bytes")
