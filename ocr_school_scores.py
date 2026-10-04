#!/usr/bin/env python3
"""
OCR 识别研招网复试分数线图片，提取结构化数据

依赖: pip install rapidocr-onnxruntime opencv-python
      (如需中国镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ rapidocr-onnxruntime)

使用:
  pip install rapidocr-onnxruntime opencv-python
  python ocr_school_scores.py
"""
import json
import os
import re
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "data", "score_lines", "images")
OUT_PATH = os.path.join(BASE_DIR, "data", "score_lines", "ocr_results.json")

KNOWN_DISCIPLINES = sorted([
    "哲学", "经济学", "法学", "教育学", "文学", "历史学",
    "理学", "工学", "农学", "医学", "军事学", "管理学", "艺术学",
    "交叉学科", "体育学",
    "金融", "应用统计", "税务", "国际商务", "保险", "资产评估", "审计",
    "法律", "社会工作", "警务", "教育", "体育", "汉语国际教育", "应用心理",
    "翻译", "新闻与传播", "出版", "文物与博物馆", "建筑学", "城市规划",
    "电子信息", "机械", "材料与化工", "资源与环境", "能源动力",
    "土木水利", "生物与医药", "交通运输", "农业", "兽医",
    "风景园林", "林业", "临床医学", "口腔医学", "公共卫生",
    "护理", "药学", "中药学", "中医", "工商管理", "公共管理",
    "会计", "旅游管理", "图书情报", "工程管理", "艺术",
    "少数民族高层次骨干人才计划", "退役大学生士兵计划",
    "强军计划", "单独考试", "援藏计划",
    # 带修饰的变体 (OCR可能识别到)
    "金融硕士", "税务硕士", "保险硕士", "国际商务硕士",
    "应用统计硕士", "审计硕士", "法律硕士", "社会工作硕士",
    "体育硕士", "汉语国际教育硕士", "应用心理硕士", "翻译硕士",
    "新闻与传播硕士", "文物与博物馆硕士", "电子信息硕士",
    "机械硕士", "风景园林硕士", "临床医学硕士", "药学硕士",
    "公共卫生硕士", "护理硕士", "口腔医学硕士", "工商管理硕士",
    "公共管理硕士", "会计硕士", "艺术硕士", "工程管理硕士",
], key=lambda x: -len(x))  # 长优先，避免"理学"误匹配"管理学"


def imread_chinese(path):
    """读取含中文路径的图片"""
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def preprocess(img):
    """预处理图片提高OCR准确率"""
    h, w = img.shape[:2]
    if w < 1000:
        scale = 1500 / w
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
    return denoised


def ocr_image(img_path, engine):
    """对图片进行OCR，返回按行组织的文本"""
    img = imread_chinese(img_path)
    if img is None:
        return None, []

    processed = preprocess(img)
    result, _ = engine(processed)

    if not result:
        return img, []

    # 按 Y 坐标分组为行
    lines = {}
    for box, text, conf in result:
        if not text or not text.strip():
            continue
        y_center = (box[0][1] + box[2][1]) / 2
        # 找最近的已有行 (Y 坐标差 < 15px 视为同行)
        matched = False
        for row_y in lines:
            if abs(y_center - row_y) < 15:
                lines[row_y].append((box[0][0], text.strip()))
                matched = True
                break
        if not matched:
            lines[y_center] = [(box[0][0], text.strip())]

    # 按 Y 坐标排序行，每行按 X 排序
    sorted_lines = []
    for y in sorted(lines.keys()):
        items = sorted(lines[y], key=lambda x: x[0])
        line_text = " ".join(t for _, t in items)
        sorted_lines.append(line_text)

    return img, sorted_lines


def parse_score_table(lines):
    """从OCR文本行中解析分数表格"""
    results = []
    current_discipline = None
    pending_discipline = None

    for line in lines:
        # 跳过纯表头行（但不跳包含学科名的行）
        has_discipline = any(d in line for d in KNOWN_DISCIPLINES)
        if not has_discipline:
            if not re.search(r"\d{2,3}", line):
                # 无学科无数字 = 纯文本说明，跳过
                continue
            if any(kw in line for kw in ["考试科目", "学科门类", "专项计划 分数线", "备注", "政治或"]):
                continue

        # 检测表头行
        if any(kw in line for kw in ["考试科目", "政治", "外语", "专业课", "综合", "备注", "学科门类"]) \
           and not has_discipline and not re.search(r"\d{2,3}", line):
            continue

        # 查找学科名 (最长优先，已在KNOWN_DISCIPLINES排序)
        found_discipline = None
        for d in KNOWN_DISCIPLINES:
            if d in line:
                found_discipline = d
                break

        # 提取数字
        numbers = re.findall(r"\d{2,3}", line)
        nums = [int(n) for n in numbers] if numbers else []

        if found_discipline:
            current_discipline = found_discipline
            if nums and len(nums) >= 2:
                results.append({
                    "discipline": current_discipline,
                    "scores": nums,
                    "raw": line,
                })
                pending_discipline = None
            else:
                pending_discipline = current_discipline
        elif nums and len(nums) >= 2:
            if pending_discipline:
                results.append({
                    "discipline": pending_discipline,
                    "scores": nums,
                    "raw": line,
                })
                current_discipline = pending_discipline
                pending_discipline = None
            elif current_discipline:
                results.append({
                    "discipline": current_discipline,
                    "scores": nums,
                    "raw": line,
                })

    return results


def ocr_all_schools():
    """批量OCR所有自划线高校图片"""
    from rapidocr_onnxruntime import RapidOCR

    if not os.path.exists(IMG_DIR):
        print("图片目录不存在，请先运行 download_score_images.py")
        return None

    school_dirs = sorted([
        d for d in os.listdir(IMG_DIR)
        if os.path.isdir(os.path.join(IMG_DIR, d))
        and d != "national_line_pdfs"
    ])

    print(f"RapidOCR 引擎已就绪")
    print(f"图片目录: {IMG_DIR}")
    print(f"找到 {len(school_dirs)} 所学校")
    print()

    engine = RapidOCR()
    all_results = {}
    total_imgs = 0
    total_with_data = 0

    for i, school_name in enumerate(school_dirs):
        t0 = time.time()
        print(f"[{i+1}/{len(school_dirs)}] {school_name}")
        school_dir = os.path.join(IMG_DIR, school_name)

        images = sorted([
            f for f in os.listdir(school_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
        ])

        school_results = []
        for img_file in images:
            img_path = os.path.join(school_dir, img_file)
            total_imgs += 1
            print(f"  {img_file[:60]}...", end=" ", flush=True)

            try:
                _, lines = ocr_image(img_path, engine)
            except Exception as e:
                print(f"✗ {e}")
                school_results.append({"image": img_file, "error": str(e), "parsed": []})
                continue

            if not lines:
                print("(空白)")
                school_results.append({"image": img_file, "text": "", "parsed": []})
            else:
                parsed = parse_score_table(lines)
                print(f"({len(parsed)} 条)")
                if parsed:
                    total_with_data += 1
                school_results.append({
                    "image": img_file,
                    "text": "\n".join(lines[:60]),
                    "parsed": parsed,
                })

        elapsed = time.time() - t0
        all_results[school_name] = school_results
        print(f"  耗时 {elapsed:.1f}s, {len(images)} 张图, {sum(1 for r in school_results if r.get('parsed'))} 张有数据")
        print()

    # 保存
    output = {
        "source": "研招网34所自划线高校复试分数线图片OCR (RapidOCR)",
        "totalImages": total_imgs,
        "imagesWithData": total_with_data,
        "schools": all_results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"OCR 完成!")
    print(f"  图片总数: {total_imgs}")
    print(f"  识别到数据: {total_with_data} 张")
    print(f"  结果: {OUT_PATH}")

    return all_results


def preview_school(school_name, max_imgs=2):
    """预览某所学校的OCR结果"""
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    school_dir = os.path.join(IMG_DIR, school_name)
    if not os.path.exists(school_dir):
        print(f"学校目录不存在: {school_dir}")
        return

    images = sorted([
        f for f in os.listdir(school_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
    ])[:max_imgs]

    for img_file in images:
        img_path = os.path.join(school_dir, img_file)
        print(f"\n{'='*60}")
        print(f"  {img_file}")
        print(f"{'='*60}")

        _, lines = ocr_image(img_path, engine)
        for line in lines:
            print(f"  {line}")

        print()
        parsed = parse_score_table(lines)
        if parsed:
            print("  解析结果:")
            for item in parsed:
                print(f"    {item['discipline']}: {item['scores']}")
        else:
            print("  (未解析出结构化数据)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="OCR 研招网复试分数线图片")
    ap.add_argument("--preview", "-p", type=str, help="预览某所学校 (学校名)")
    ap.add_argument("--all", "-a", action="store_true", default=True, help="批量处理全部")
    args = ap.parse_args()

    print("考研复试分数线图片OCR识别器 (RapidOCR)")
    print()

    if args.preview:
        preview_school(args.preview)
    else:
        ocr_all_schools()
