#!/usr/bin/env python3
"""
研招网录取分数线采集器
数据来源: https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml
采集内容:
  1. 国家线 (统一划线 + 单独划线 + 照顾政策)
  2. 34所自划线高校复试分数线链接
  3. 各年度国家线文章
输出: data/score_lines/*.json
"""
import json
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# Fix Windows terminal encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml",
}
LNFSX_URL = "https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "score_lines")
REQUEST_DELAY = 0.5


def fetch_page(url):
    """获取页面HTML"""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.encoding = "utf-8"
    return r.text


def parse_js_list(js_text, var_name):
    """从JS文本中提取指定变量的数组值（处理非标准JSON）"""
    pattern = rf"var\s+{var_name}\s*=\s*(\[[\s\S]*?\]);"
    m = re.search(pattern, js_text)
    if not m:
        print(f"  [WARN] 未找到变量: {var_name}")
        return []

    raw = m.group(1)
    # 将JS对象转为JSON兼容格式
    # 1. 处理单引号key和不加引号的key
    raw = re.sub(r"'", '"', raw)
    raw = re.sub(r'(\s+)([a-zA-Z_]\w*)(\s*:)', r'\1"\2"\3', raw)
    # 2. 移除尾随逗号（JSON不允许）
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    # 3. 处理URL中的反斜杠
    raw = raw.replace('\\', '')

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON解析 {var_name} 失败: {e}")
        # 保存原始数据以便调试
        debug_path = os.path.join(OUT_DIR, f"_debug_{var_name}.txt")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"    原始数据已保存至 {debug_path}")
        return []


def scrape_national_lines():
    """采集国家线数据"""
    print("=" * 60)
    print("采集国家线数据（近五年研考分数线及趋势图）")
    print(f"来源: {LNFSX_URL}")
    print()

    html = fetch_page(LNFSX_URL)
    print(f"  页面长度: {len(html)} 字符")

    # 提取所有 <script> 内容
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL)
    js_text = "\n".join(s for s in scripts if len(s) > 1000)
    print(f"  提取JS脚本: {len(scripts)} 段，合并后 {len(js_text)} 字符")

    result = {
        "source": LNFSX_URL,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "description": "研招网近五年考研国家线及趋势图数据（2022-2026）",
    }

    # 1. 解析年度列表
    year_list = parse_js_list(js_text, "yearList")
    result["years"] = year_list
    print(f"  ✓ 年度列表: {len(year_list)} 年")

    # 2. 解析统一划线 (学术学位)
    tyhx = parse_js_list(js_text, "tyhxList")
    result["unified_lines"] = tyhx
    print(f"  ✓ 统一划线（学术学位）: {len(tyhx)} 个学科门类")
    for item in tyhx:
        name = item.get("name", "")
        scores_a = item.get("gjx", {}).get("typea", [])
        print(f"    - {name}: A区总分 {scores_a}")

    # 3. 解析单独划线 (专业学位)
    ddhx = parse_js_list(js_text, "ddhxList")
    result["separate_lines"] = ddhx
    print(f"  ✓ 单独划线（专业学位）: {len(ddhx)} 个专业类别")
    for item in ddhx:
        name = item.get("name", "")
        print(f"    - {name}")

    # 4. 解析照顾政策
    zgzc = parse_js_list(js_text, "zgzcList")
    result["preferential_policies"] = zgzc
    print(f"  ✓ 照顾政策: {len(zgzc)} 条")

    # 保存
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "national_lines.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ 国家线数据已保存: {out_path}")

    return result


def scrape_self_determined_lines():
    """采集34所自划线高校复试分数线"""
    print()
    print("=" * 60)
    print("采集34所自划线高校复试分数线链接")
    print(f"来源: {LNFSX_URL}")
    print()

    html = fetch_page(LNFSX_URL)
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL)
    js_text = "\n".join(s for s in scripts if len(s) > 1000)

    zhx = parse_js_list(js_text, "zhxList")
    print(f"  自划线高校: {len(zhx)} 所")
    for school in zhx:
        name = school.get("yxmc", "")
        years = [y["year"] for y in school.get("yearList", [])]
        print(f"    - {name}: {', '.join(years)} 年")

    result = {
        "source": LNFSX_URL,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "description": "34所自划线高校复试分数线链接（2022-2026）",
        "schools": zhx,
        "count": len(zhx),
    }

    out_path = os.path.join(OUT_DIR, "self_determined_lines.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ 自划线高校数据已保存: {out_path}")

    return result


def scrape_school_score_detail(school_name, year, article_url):
    """
    抓取自划线高校某年的具体分数线文章
    研招网的自划线文章通常以表格形式呈现各学科的复试基本分数线
    """
    try:
        html = fetch_page(article_url)
        soup = BeautifulSoup(html, "html.parser")

        # 寻找文章主体内容
        content_div = None
        for div in soup.find_all("div"):
            cls = " ".join(div.get("class", []))
            if any(k in cls for k in ["article", "content", "main"]):
                content_div = div
                break

        if not content_div:
            content_div = soup

        # 提取表格数据
        tables = content_div.find_all("table")
        score_data = []
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            headers = []
            for th in rows[0].find_all(["th", "td"]):
                headers.append(th.get_text(strip=True))

            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    row_data = {}
                    for j, cell in enumerate(cells):
                        key = headers[j] if j < len(headers) else f"col{j}"
                        row_data[key] = cell.get_text(strip=True)
                    if row_data:
                        score_data.append(row_data)

        # 提取所有段落文本（有些数据用图片而非表格）
        paragraphs = []
        for p in content_div.find_all(["p", "div"]):
            text = p.get_text(strip=True)
            if len(text) > 20:
                paragraphs.append(text)

        return {
            "school": school_name,
            "year": year,
            "url": article_url,
            "tables": score_data,
            "text_content": paragraphs[:20],
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        return {
            "school": school_name,
            "year": year,
            "url": article_url,
            "error": str(e),
        }


def scrape_all_self_determined_scores(years=None):
    """
    采集所有34所自划线高校的具体分数线
    注意：研招网文章中的具体分数线通常以图片形式展示，
    表格形式的数据有限。此函数采集可解析的结构化数据。
    """
    print()
    print("=" * 60)
    print("采集自划线高校具体分数线（HTML解析）")
    print()

    # 加载自划线高校列表
    zhx_path = os.path.join(OUT_DIR, "self_determined_lines.json")
    if not os.path.exists(zhx_path):
        print("  请先运行 scrape_self_determined_lines()")
        return []

    with open(zhx_path, "r", encoding="utf-8") as f:
        zhx_data = json.load(f)

    schools = zhx_data["schools"]
    if years is None:
        years = ["2026", "2025", "2024"]

    all_scores = []
    total = len(schools) * len(years)
    count = 0

    for school in schools:
        name = school["yxmc"]
        year_urls = {y["year"]: y["url"] for y in school["yearList"]}

        for year in years:
            count += 1
            if year not in year_urls:
                continue

            url = year_urls[year]
            print(f"  [{count}/{total}] {name} {year}年...", end=" ", flush=True)

            data = scrape_school_score_detail(name, year, url)
            if "error" in data:
                print(f"✗ {data['error']}")
            else:
                tables_count = len(data.get("tables", []))
                print(f"✓ ({tables_count} 个表格)")
                all_scores.append(data)

            time.sleep(REQUEST_DELAY)

    result = {
        "source": "研招网自划线高校复试分数线文章",
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(all_scores),
        "schools_scored": len(set(s["school"] for s in all_scores if "error" not in s)),
        "scores": all_scores,
    }

    out_path = os.path.join(OUT_DIR, "self_determined_scores_detail.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ 自划线详细数据已保存: {out_path}")

    return result


def export_to_csv():
    """将国家线数据导出为易读的CSV格式"""
    print()
    print("=" * 60)
    print("导出国家线为CSV")

    nl_path = os.path.join(OUT_DIR, "national_lines.json")
    if not os.path.exists(nl_path):
        print("  请先运行 scrape_national_lines()")
        return

    with open(nl_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    years = ["2022", "2023", "2024", "2025", "2026"]

    # 1. 国家线总分趋势 CSV
    total_csv = os.path.join(OUT_DIR, "national_lines_total.csv")
    with open(total_csv, "w", encoding="utf-8-sig") as f:
        f.write("类别,学科/专业," + ",".join(f"A区{y}" for y in years) + "," +
                ",".join(f"B区{y}" for y in years) + "\n")

        for item in data.get("unified_lines", []):
            name = item["name"]
            gjx = item.get("gjx", {})
            typea = gjx.get("typea", [])
            typeb = gjx.get("typeb", [])
            f.write(f"学术学位,{name}," +
                    ",".join(str(v) for v in typea) + "," +
                    ",".join(str(v) for v in typeb) + "\n")

        for item in data.get("separate_lines", []):
            name = item["name"]
            gjx = item.get("gjx", {})
            typea = gjx.get("typea", [])
            typeb = gjx.get("typeb", [])
            f.write(f"专业学位,{name}," +
                    ",".join(str(v) for v in typea) + "," +
                    ",".join(str(v) for v in typeb) + "\n")

    print(f"  ✓ 总分CSV: {total_csv}")

    # 2. 国家线单科分数 CSV
    single_csv = os.path.join(OUT_DIR, "national_lines_single_subject.csv")
    with open(single_csv, "w", encoding="utf-8-sig") as f:
        f.write("类别,学科/专业,年份,A区单科1,A区单科2,B区单科1,B区单科2\n")

        for item in data.get("unified_lines", []):
            name = item["name"]
            for dk in item.get("dkx", []):
                f.write(f"学术学位,{name},{dk.get('year','')}," +
                        f"{dk.get('typeaone','')},{dk.get('typeatwo','')}," +
                        f"{dk.get('typebone','')},{dk.get('typebtwo','')}\n")

        for item in data.get("separate_lines", []):
            name = item["name"]
            for dk in item.get("dkx", []):
                f.write(f"专业学位,{name},{dk.get('year','')}," +
                        f"{dk.get('typeaone','')},{dk.get('typeatwo','')}," +
                        f"{dk.get('typebone','')},{dk.get('typebtwo','')}\n")

    print(f"  ✓ 单科CSV: {single_csv}")

    # 3. 自划线高校列表 CSV
    zx_path = os.path.join(OUT_DIR, "self_determined_lines.json")
    if os.path.exists(zx_path):
        with open(zx_path, "r", encoding="utf-8") as f:
            zx_data = json.load(f)

        zx_csv = os.path.join(OUT_DIR, "self_determined_schools.csv")
        with open(zx_csv, "w", encoding="utf-8-sig") as f:
            f.write("高校名称," + ",".join(f"{y}年链接" for y in years) + "\n")
            for school in zx_data.get("schools", []):
                name = school["yxmc"]
                urls = {y["year"]: y["url"] for y in school["yearList"]}
                f.write(f"{name}," +
                        ",".join(urls.get(y, "") for y in years) + "\n")

        print(f"  ✓ 自划线CSV: {zx_csv}")


def build_summary():
    """构建数据摘要"""
    print()
    print("=" * 60)
    print("生成数据摘要")

    nl_path = os.path.join(OUT_DIR, "national_lines.json")
    zx_path = os.path.join(OUT_DIR, "self_determined_lines.json")

    summary = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dataSources": {
            "nationalLines": LNFSX_URL,
            "selfDeterminedLines": LNFSX_URL,
        },
    }

    if os.path.exists(nl_path):
        with open(nl_path, "r", encoding="utf-8") as f:
            nl = json.load(f)
        summary["nationalLines"] = {
            "years": [y["year"] for y in nl.get("years", [])],
            "academicDisciplines": len(nl.get("unified_lines", [])),
            "professionalCategories": len(nl.get("separate_lines", [])),
            "preferentialPolicies": len(nl.get("preferential_policies", [])),
            "disciplineNames": [item["name"] for item in nl.get("unified_lines", [])],
        }

    if os.path.exists(zx_path):
        with open(zx_path, "r", encoding="utf-8") as f:
            zx = json.load(f)
        summary["selfDeterminedLines"] = {
            "totalSchools": zx.get("count", 0),
            "schoolNames": [s["yxmc"] for s in zx.get("schools", [])],
        }

    out_path = os.path.join(OUT_DIR, "summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 摘要已保存: {out_path}")

    # 打印摘要
    nl_sum = summary.get("nationalLines", {})
    zx_sum = summary.get("selfDeterminedLines", {})
    print(f"\n  📊 数据摘要:")
    print(f"    年份: {', '.join(nl_sum.get('years', []))}")
    print(f"    学术学位门类: {nl_sum.get('academicDisciplines', 0)}")
    print(f"    专业学位类别: {nl_sum.get('professionalCategories', 0)}")
    print(f"    自划线高校: {zx_sum.get('totalSchools', 0)} 所")

    return summary


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("研招网录取分数线采集器")
    print(f"输出目录: {OUT_DIR}")
    print()

    # Step 1: 采集国家线
    scrape_national_lines()

    # Step 2: 采集34所自划线高校链接
    scrape_self_determined_lines()

    # Step 3: 导出CSV
    export_to_csv()

    # Step 4: 生成摘要
    build_summary()

    print()
    print("=" * 60)
    print("采集完成！所有文件已保存至:")
    print(f"  {OUT_DIR}")
    print()
    print("文件列表:")
    for f in sorted(os.listdir(OUT_DIR)):
        path = os.path.join(OUT_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f} ({size:,} bytes)")
