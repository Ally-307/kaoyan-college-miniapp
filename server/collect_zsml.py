#!/usr/bin/env python3
"""研招网硕士专业目录采集（官方来源：https://yz.chsi.com.cn/zsml/、/sch/）"""
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "Referer": "https://yz.chsi.com.cn/zsml/",
}
DWS_URL = "https://yz.chsi.com.cn/zsml/rs/dws.do"
DWZYS_URL = "https://yz.chsi.com.cn/zsml/rs/dwzys.do"
SCHOOL_INFO = "https://yz.chsi.com.cn/sch/schoolInfo--schId-{}.dhtml"
SESSION = requests.Session()
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "collect_985.log")
PROGRESS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "collect_985.progress")
REQUEST_DELAY = 0.8

ALL_985 = {
    "北京大学", "清华大学", "浙江大学", "复旦大学", "上海交通大学", "南京大学",
    "武汉大学", "华中科技大学", "中山大学", "四川大学", "西安交通大学", "哈尔滨工业大学",
    "中国科学技术大学", "北京师范大学", "中国人民大学", "南开大学", "天津大学", "厦门大学",
    "同济大学", "吉林大学", "东南大学", "山东大学", "北京航空航天大学", "北京理工大学",
    "国防科技大学", "中国农业大学", "中央民族大学", "西北工业大学", "西北农林科技大学",
    "兰州大学", "重庆大学", "电子科技大学", "大连理工大学", "东北大学", "中南大学",
    "湖南大学", "华南理工大学",
}

PRO_CODES = [
    "125100", "125200", "125300", "125400", "125500", "125600",
    "025100", "025200", "025300", "025400",
    "035101", "035102", "045100", "045200", "045300", "045400",
    "055100", "055200", "055300",
    "085100", "085400", "085500", "085600", "085700", "085800", "085900", "086000", "086100",
    "095100", "095200", "095300",
    "105100", "105200", "105300", "105400", "105500",
]

MLMC_BY_PREFIX = {
    "01": "哲学", "02": "经济学", "03": "法学", "04": "教育学", "05": "文学",
    "06": "历史学", "07": "理学", "08": "工学", "09": "农学", "10": "医学",
    "11": "军事学", "12": "管理学", "13": "艺术学",
}


def search_schools(name):
    form = {
        "dwmc": name, "dwdm": "", "ssdm": "", "xxfs": "", "dwlxs": ["all"],
        "tydxs": "", "jsggjh": "", "start": 0, "curPage": 1, "pageSize": 20,
        "totalPage": 0, "totalCount": 0,
    }
    res = post_json(DWS_URL, form)
    if not res or not res.get("flag"):
        return None
    lst = (res.get("msg") or {}).get("list") or []
    return lst[0] if lst else None


def log(msg):
    line = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + msg
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def post_json(url, form, tries=10):
    """POST 表单并解析 JSON；触发研招网限流时指数退避重试。"""
    label = form.get("dwmc") or form.get("zymc") or url
    for attempt in range(tries):
        if attempt:
            wait = min(2 ** attempt, 60)
            log(f"[rate-limit] {label} 等待 {wait}s 重试 ({attempt + 1}/{tries})")
            time.sleep(wait)
        try:
            r = SESSION.post(url, data=form, headers=HEADERS, timeout=25)
            r.encoding = "utf-8"
            res = r.json()
        except Exception as exc:
            log(f"[retry] {label} 请求异常: {type(exc).__name__}: {exc}")
            continue
        if res.get("flag") is False and "访问太频繁" in (res.get("msg") or ""):
            log(f"[rate-limit] {label} 触发限流")
            continue
        return res
    return None


def get_text(url, tries=6):
    for attempt in range(tries):
        if attempt:
            time.sleep(min(2 ** attempt, 30))
        try:
            r = SESSION.get(url, headers=HEADERS, timeout=25)
            r.encoding = "utf-8"
            return r.text
        except Exception:
            continue
    return ""


def academic_programs(school_id):
    """从院校专业介绍页抓取学术学位专业（公开、无需登录）。"""
    text = get_text(SCHOOL_INFO.format(school_id))
    m = re.search(r"/sch/listYzZyjs--schId-{}[^\"']*categoryId-(\d+)".format(re.escape(school_id)), text)
    if not m:
        return []
    url = f"https://yz.chsi.com.cn/sch/listYzZyjs--schId-{school_id},categoryId-{m.group(1)}.dhtml"
    html = get_text(url)
    if not html:
        return []
    html = html.split("<h3>博士专业", 1)[0]
    items = re.findall(r"([\u4e00-\u9fffA-Za-z（）()·]+)\[(\d{6})\]", html)
    seen = set()
    result = []
    for name, code in items:
        if code in seen:
            continue
        seen.add(code)
        result.append({
            "zydm": code,
            "zymc": name,
            "xwlx": "xs",
            "xwlxmc": "学术学位",
            "mlmc": MLMC_BY_PREFIX.get(code[:2], ""),
            "sourceUrl": url,
        })
    return result


def professional_programs(item, code):
    form = {
        "dwdm": item.get("dwdm") or "",
        "dwmc": item.get("dwmc") or "",
        "zydm": code,
        "zymc": "",
        "xwlx": "",
        "mldm": "",
        "yjxkdm": "",
        "xxfs": "",
        "tydxs": "",
        "jsggjh": "",
        "start": 0,
        "curPage": 1,
        "pageSize": 10,
        "totalPage": 0,
        "totalCount": 0,
    }
    res = post_json(DWZYS_URL, form)
    if not res or not res.get("flag"):
        return []
    lst = (res.get("msg") or {}).get("list") or []
    for p in lst:
        p["sourceUrl"] = f"https://yz.chsi.com.cn/zsml/dwzy.do?schId={item.get('schId')}"
    return lst


def collect_schools(schools, out_path, delay=REQUEST_DELAY, resume=False):
    get_text("https://yz.chsi.com.cn/zsml/dw.do")
    records = []
    if resume and os.path.exists(out_path):
        try:
            with open(out_path, encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []
    done_ids = {r.get("schoolId") for r in records}
    skipped = []
    failed = []
    total = len(schools)
    start_ts = time.time()

    def write_progress(current="", programs=0, processed=0):
        state = {
            "running": True,
            "startedAt": datetime.now(timezone.utc).isoformat(),
            "done": len(records),
            "total": total,
            "processed": processed,
            "percent": 100 * processed // max(total, 1),
            "school": current,
            "programs": programs,
            "skipped": skipped,
            "failed": failed,
            "elapsedSec": int(time.time() - start_ts),
        }
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)

    write_progress(current="初始化" if not records else f"续跑：已完成 {len(records)} 所")
    for i, school in enumerate(schools):
        if school["id"] in done_ids:
            log(f"[{i + 1}/{total}] 跳过（已有数据）: {school['name']}")
            continue
        processed = i + 1
        write_progress(current=school["name"], processed=processed)
        try:
            item = search_schools(school["name"])
            if not item:
                skipped.append(school["name"])
                log(f"[skip] {school['name']}: 研招网未匹配")
                write_progress(current=school["name"], processed=processed)
                continue
            programs = academic_programs(school["id"])
            for code in PRO_CODES:
                found = professional_programs(item, code)
                programs.extend(found)
                time.sleep(delay)
            # 去重：同代码同学位类型只保留一条
            seen = set()
            unique = []
            for p in programs:
                key = (p.get("zydm"), p.get("xwlx"))
                if key in seen:
                    continue
                seen.add(key)
                unique.append(p)
            records.append({
                "schoolId": school["id"],
                "name": school["name"],
                "dwdm": item.get("dwdm"),
                "fetchedAt": datetime.now(timezone.utc).isoformat(),
                "sourceUrl": f"https://yz.chsi.com.cn/zsml/dwzy.do?schId={school['id']}",
                "programs": unique,
            })
            percent = 100 * processed // total
            log(f"[{processed}/{total}] ({percent}%) {school['name']}: {len(unique)} 个真实专业")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            write_progress(current=school["name"], programs=len(unique), processed=processed)
            time.sleep(delay)
        except Exception as exc:
            failed.append(school["name"])
            log(f"[error] {school['name']}: {exc}")
            write_progress(current=school["name"], processed=processed)

    final = {
        "running": False,
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "done": len(records),
        "total": total,
        "processed": total,
        "percent": 100 if len(records) == total else 100 * len(records) // max(total, 1),
        "school": "",
        "programs": 0,
        "skipped": skipped,
        "failed": failed,
        "elapsedSec": int(time.time() - start_ts),
    }
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False)
    return records


def load_schools():
    path = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json"
    return json.load(open(path, encoding="utf-8"))["schools"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="采集研招网硕士专业目录")
    parser.add_argument("--scope", choices=["test", "985", "all"], default="test")
    parser.add_argument("--resume", action="store_true", help="跳过已采集成功的学校")
    args = parser.parse_args()

    schools = load_schools()
    if args.scope == "985":
        schools = [s for s in schools if s["name"] in ALL_985]
    elif args.scope == "test":
        schools = [s for s in schools if s["name"] == "北京大学"]

    out = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\data\raw_zsml_programs.json"
    records = collect_schools(schools, out, resume=args.resume)
    print(f"[完成] 共 {len(records)} 所学校，输出 {out}", flush=True)
