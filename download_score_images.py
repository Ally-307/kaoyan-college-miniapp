#!/usr/bin/env python3
"""
批量下载34所自划线高校复试分数线图片 + 国家线PDF
"""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://yz.chsi.com.cn/kyzx/zt/lnfsx2026.shtml",
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "data", "score_lines", "images")
REQUEST_DELAY = 0.3


def download_file(url, path):
    """下载文件，跳过已存在的"""
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return False, "skipped"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200 and len(r.content) > 100:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(r.content)
            return True, f"{len(r.content)} bytes"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


def download_all_self_determined_images():
    """下载所有34所自划线高校的复试线图片"""
    print("=" * 60)
    print("批量下载34所自划线高校复试分数线图片")
    print()

    # 加载自划线高校数据
    zx_path = os.path.join(BASE_DIR, "data", "score_lines", "self_determined_lines.json")
    if not os.path.exists(zx_path):
        print("请先运行 scrape_score_lines.py")
        return

    with open(zx_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schools = data["schools"]
    total_imgs = 0
    total_articles = 0

    for school in schools:
        name = school["yxmc"]
        print(f"\n{'='*40}")
        print(f"  {name}")
        print(f"{'='*40}")

        for year_info in school["yearList"]:
            year = year_info["year"]
            article_url = year_info["url"]

            print(f"  [{year}] 获取文章...", end=" ", flush=True)
            total_articles += 1

            try:
                r = requests.get(article_url, headers=HEADERS, timeout=30)
                r.encoding = "utf-8"
            except Exception as e:
                print(f"✗ 文章请求失败: {e}")
                time.sleep(REQUEST_DELAY * 2)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            time.sleep(REQUEST_DELAY)

            # 查找文章正文中的所有图片
            img_count = 0
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "")

                # 跳过 LOGO、二维码等无关图片
                if any(skip in src.lower() for skip in ["logo", "qrcode", "erweima", "icon", "qr", "banner", "nav"]):
                    continue
                if not src or src.endswith((".svg",)):
                    continue

                # 补全 URL
                if src.startswith("//"):
                    src = "https:" + src
                elif not src.startswith("http"):
                    if src.startswith("/"):
                        src = "https://yz.chsi.com.cn" + src
                    else:
                        src = "https://yz.chsi.com.cn/" + src

                # 构建文件名
                ext = src.split(".")[-1].split("?")[0]
                if ext not in ("png", "jpg", "jpeg", "gif", "bmp"):
                    ext = "jpg"

                safe_name = f"{name}_{year}"
                if alt and len(alt) < 30:
                    safe_name += f"_{alt}"
                safe_name = re.sub(r'[\\/:*?"<>|]', '_', safe_name)
                fname = f"{safe_name}_{img_count}.{ext}"
                path = os.path.join(OUT_DIR, name, fname)

                ok, info = download_file(src, path)
                if ok:
                    img_count += 1
                    total_imgs += 1

            print(f"{img_count} 张图片", end="", flush=True)
            if img_count == 0:
                print()

    print(f"\n{'='*60}")
    print(f"下载完成: {total_articles} 篇文章, {total_imgs} 张图片")
    print(f"保存路径: {OUT_DIR}")


def download_national_line_pdf():
    """下载年度国家线PDF文件"""
    print()
    print("=" * 60)
    print("下载国家线PDF")
    print()

    pdf_dir = os.path.join(OUT_DIR, "national_line_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    with open(os.path.join(BASE_DIR, "data", "score_lines", "national_lines.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    # 从年度列表中下载每篇文章的PDF
    for year_info in data.get("years", []):
        year = year_info["year"]
        url = year_info["url"]
        print(f"  [{year}] 获取文章: {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.encoding = "utf-8"
        except Exception as e:
            print(f"    ✗ 请求失败: {e}")
            continue

        # 查找PDF下载链接
        soup = BeautifulSoup(r.text, "html.parser")
        pdf_found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".pdf" in href.lower():
                if href.startswith("//"):
                    href = "https:" + href
                elif not href.startswith("http"):
                    href = "https://yz.chsi.com.cn" + href

                fname = f"国家线_{year}.pdf"
                path = os.path.join(pdf_dir, fname)
                ok, info = download_file(href, path)
                status = "✓" if ok else info
                print(f"    PDF: {fname} - {status}")
                pdf_found += 1

        time.sleep(REQUEST_DELAY)
        if pdf_found == 0:
            print(f"    (无PDF下载链接)")

    print(f"\n  PDF保存路径: {pdf_dir}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("研招网复试分数线图片批量下载")
    print()

    download_all_self_determined_images()
    download_national_line_pdf()

    # 统计
    print()
    print("=" * 60)
    print("下载统计")
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(OUT_DIR):
        for f in files:
            path = os.path.join(root, f)
            total_size += os.path.getsize(path)
            file_count += 1
    print(f"  文件总数: {file_count}")
    print(f"  总大小: {total_size / 1024 / 1024:.1f} MB")
    print(f"  保存路径: {OUT_DIR}")
