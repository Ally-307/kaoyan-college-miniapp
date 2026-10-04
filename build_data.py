import json

# Build complete data programmatically to avoid encoding issues
data = {"schools": []}

# First read existing data (清华大学 already generated)
fp = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json"
with open(fp, "r", encoding="utf-8") as f:
    data = json.load(f)

# ===== School 2: 北京大学 =====
pku = {
    "id": "10002", "name": "北京大学", "province": "北京", "city": "北京",
    "region": "华北", "type": ["985", "211", "双一流"],
    "intro": "北京大学创立于1898年，是中国第一所国立综合性大学。北大是中国现代高等教育的奠基者，以\u300c思想自由，兼容并包\u300d的学术精神著称。",
    "tags": ["顶尖985", "C9"],
    "majors": [
        {
            "id": "10002_030100", "name": "法学", "code": "030100",
            "category": "法学", "degreeType": "学术学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "201", "name": "英语（一）", "type": "统考", "score": 100, "order": 2},
                    {"code": "646", "name": "法学综合", "type": "自命题", "score": 150, "order": 3},
                    {"code": "930", "name": "法学专业卷", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["法学综合面试", "英语口语"], "ratio": "1.5:1", "method": "面试"},
            "admissionData": [
                {"year": 2026, "reexamLine": 370, "minAdmissionScore": 385, "maxAdmissionScore": 420, "reexamCount": 24, "admissionCount": 16, "applicationCount": 450},
                {"year": 2025, "reexamLine": 365, "minAdmissionScore": 372, "maxAdmissionScore": 415, "reexamCount": 22, "admissionCount": 15, "applicationCount": 420}
            ],
            "duration": "3年", "tuition": "8000元/年",
            "crossMajorPolicy": "接受跨考", "equivalentEducationPolicy": "需加试2门本科主干课程",
            "accommodation": "提供住宿，4人间为主",
            "tags": ["顶尖", "竞争激烈"]
        },
        {
            "id": "10002_025100", "name": "金融", "code": "025100",
            "category": "经济学", "degreeType": "专业学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "204", "name": "英语（二）", "type": "统考", "score": 100, "order": 2},
                    {"code": "396", "name": "经济类综合能力", "type": "统考", "score": 150, "order": 3},
                    {"code": "431", "name": "金融学综合", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["金融学", "经济学基础", "英语口语"], "ratio": "1.4:1", "method": "面试（含英语口试）"},
            "admissionData": [
                {"year": 2026, "reexamLine": 390, "minAdmissionScore": 398, "maxAdmissionScore": 445, "reexamCount": 55, "admissionCount": 40, "applicationCount": 1200},
                {"year": 2025, "reexamLine": 385, "minAdmissionScore": 392, "maxAdmissionScore": 438, "reexamCount": 50, "admissionCount": 38, "applicationCount": 1150}
            ],
            "duration": "2年", "tuition": "99000元/年",
            "crossMajorPolicy": "接受跨考", "equivalentEducationPolicy": "不接受同等学力报考",
            "accommodation": "汇丰商学院在深圳，提供住宿",
            "tags": ["热门", "竞争激烈"]
        }
    ]
}
data["schools"].append(pku)

# ===== School 3: 浙江大学 ======
zju = {
    "id": "10003", "name": "浙江大学", "province": "浙江", "city": "杭州",
    "region": "华东", "type": ["985", "211", "双一流"],
    "intro": "浙江大学是教育部直属的综合性全国重点大学，坐落于历史文化名城杭州。前身是1897年创建的求是书院，是中国人自己最早创办的新式高等学校之一。",
    "tags": ["顶尖985", "C9"],
    "majors": [
        {
            "id": "10003_081200", "name": "计算机科学与技术", "code": "081200",
            "category": "工学", "degreeType": "学术学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "201", "name": "英语（一）", "type": "统考", "score": 100, "order": 2},
                    {"code": "301", "name": "数学（一）", "type": "统考", "score": 150, "order": 3},
                    {"code": "408", "name": "计算机学科专业基础综合", "type": "统考", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["程序设计", "数据结构", "算法设计"], "ratio": "1.4:1", "method": "笔试+面试"},
            "admissionData": [
                {"year": 2026, "reexamLine": 370, "minAdmissionScore": 382, "maxAdmissionScore": 430, "reexamCount": 35, "admissionCount": 25, "applicationCount": 520},
                {"year": 2025, "reexamLine": 365, "minAdmissionScore": 375, "maxAdmissionScore": 425, "reexamCount": 32, "admissionCount": 22, "applicationCount": 480}
            ],
            "duration": "3年", "tuition": "8000元/年",
            "crossMajorPolicy": "接受跨考，需在复试中加试",
            "equivalentEducationPolicy": "需加试2门本科主干课程",
            "accommodation": "提供住宿，3-4人间",
            "tags": ["顶尖", "竞争激烈"]
        }
    ]
}
data["schools"].append(zju)

# ===== School 4: 复旦大学 ======
fudan = {
    "id": "10004", "name": "复旦大学", "province": "上海", "city": "上海",
    "region": "华东", "type": ["985", "211", "双一流"],
    "intro": "复旦大学创建于1905年，原名复旦公学，是中国人自主创办的第一所高等院校。位于上海市，是一所世界知名、国内顶尖的综合性研究型大学。",
    "tags": ["顶尖985", "C9"],
    "majors": [
        {
            "id": "10004_025100", "name": "金融", "code": "025100",
            "category": "经济学", "degreeType": "专业学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "204", "name": "英语（二）", "type": "统考", "score": 100, "order": 2},
                    {"code": "396", "name": "经济类综合能力", "type": "统考", "score": 150, "order": 3},
                    {"code": "431", "name": "金融学综合", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["投资学", "公司金融", "英语口语"], "ratio": "1.3:1", "method": "面试（含英语口试）"},
            "admissionData": [
                {"year": 2026, "reexamLine": 395, "minAdmissionScore": 402, "maxAdmissionScore": 450, "reexamCount": 60, "admissionCount": 46, "applicationCount": 1500},
                {"year": 2025, "reexamLine": 390, "minAdmissionScore": 398, "maxAdmissionScore": 442, "reexamCount": 55, "admissionCount": 42, "applicationCount": 1400}
            ],
            "duration": "2年", "tuition": "126000元/年",
            "crossMajorPolicy": "接受跨考", "equivalentEducationPolicy": "不接受同等学力报考",
            "accommodation": "不提供住宿（专业学位）",
            "tags": ["热门", "竞争激烈"]
        },
        {
            "id": "10004_055200", "name": "新闻与传播", "code": "055200",
            "category": "文学", "degreeType": "专业学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "204", "name": "英语（二）", "type": "统考", "score": 100, "order": 2},
                    {"code": "334", "name": "新闻与传播专业综合能力", "type": "自命题", "score": 150, "order": 3},
                    {"code": "440", "name": "新闻与传播专业基础", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["新闻传播学综合", "新闻实务", "英语口语"], "ratio": "1.3:1", "method": "面试+笔试"},
            "admissionData": [
                {"year": 2026, "reexamLine": 380, "minAdmissionScore": 385, "maxAdmissionScore": 420, "reexamCount": 40, "admissionCount": 30, "applicationCount": 800},
                {"year": 2025, "reexamLine": 375, "minAdmissionScore": 380, "maxAdmissionScore": 415, "reexamCount": 38, "admissionCount": 28, "applicationCount": 750}
            ],
            "duration": "2年", "tuition": "96000元/年",
            "crossMajorPolicy": "接受跨考", "equivalentEducationPolicy": "需加试",
            "accommodation": "不提供住宿",
            "tags": ["热门"]
        }
    ]
}
data["schools"].append(fudan)

# ===== School 5: 上海交通大学 ======
sjtu = {
    "id": "10005", "name": "上海交通大学", "province": "上海", "city": "上海",
    "region": "华东", "type": ["985", "211", "双一流"],
    "intro": "上海交通大学是我国历史最悠久、享誉海内外的高等学府之一。是一所\u300c综合性、研究型、国际化\u300d的国内一流、国际知名大学。",
    "tags": ["顶尖985", "C9"],
    "majors": [
        {
            "id": "10005_080200", "name": "机械工程", "code": "080200",
            "category": "工学", "degreeType": "学术学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "201", "name": "英语（一）", "type": "统考", "score": 100, "order": 2},
                    {"code": "301", "name": "数学（一）", "type": "统考", "score": 150, "order": 3},
                    {"code": "809", "name": "机械设计与控制理论基础", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["机械原理", "机械设计", "工程力学"], "ratio": "1.3:1", "method": "笔试+面试"},
            "admissionData": [
                {"year": 2026, "reexamLine": 355, "minAdmissionScore": 365, "maxAdmissionScore": 410, "reexamCount": 40, "admissionCount": 30, "applicationCount": 480},
                {"year": 2025, "reexamLine": 350, "minAdmissionScore": 360, "maxAdmissionScore": 405, "reexamCount": 38, "admissionCount": 28, "applicationCount": 450}
            ],
            "duration": "2.5年", "tuition": "8000元/年",
            "crossMajorPolicy": "接受相关专业跨考", "equivalentEducationPolicy": "需加试2门",
            "accommodation": "提供住宿",
            "tags": ["强势学科"]
        },
        {
            "id": "10005_085402", "name": "电子与通信工程", "code": "085402",
            "category": "工学", "degreeType": "专业学位", "studyMode": "全日制",
            "initialExam": {
                "subjects": [
                    {"code": "101", "name": "思想政治理论", "type": "统考", "score": 100, "order": 1},
                    {"code": "201", "name": "英语（一）", "type": "统考", "score": 100, "order": 2},
                    {"code": "301", "name": "数学（一）", "type": "统考", "score": 150, "order": 3},
                    {"code": "819", "name": "信号系统与信号处理", "type": "自命题", "score": 150, "order": 4}
                ], "totalScore": 500
            },
            "reexam": {"subjects": ["数字信号处理", "通信原理", "英语口语"], "ratio": "1.3:1", "method": "面试+笔试"},
            "admissionData": [
                {"year": 2026, "reexamLine": 360, "minAdmissionScore": 375, "maxAdmissionScore": 420, "reexamCount": 50, "admissionCount": 38, "applicationCount": 600},
                {"year": 2025, "reexamLine": 355, "minAdmissionScore": 368, "maxAdmissionScore": 415, "reexamCount": 45, "admissionCount": 35, "applicationCount": 550}
            ],
            "duration": "2.5年", "tuition": "10000元/年",
            "crossMajorPolicy": "接受电子电气相关专业跨考", "equivalentEducationPolicy": "不接受",
            "accommodation": "提供住宿",
            "tags": ["热门"]
        }
    ]
}
data["schools"].append(sjtu)

# Write JSON
json_str = json.dumps(data, ensure_ascii=False, indent=2)
validated = json.loads(json_str)
print(f"Data valid! Schools: {len(validated['schools'])}, Majors: {sum(len(s['majors']) for s in validated['schools'])}")

with open(fp, "w", encoding="utf-8") as f:
    f.write(json_str)
print("Saved schools.json")

# Also generate schools.js for WeChat Mini Program (require only supports .js files)
js_path = fp.replace("schools.json", "schools.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write("var schoolData = " + json_str + ";\nmodule.exports = schoolData;\n")
print("Saved schools.js")
