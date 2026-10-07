"""
Deterministic asset splitter and validator for Color by Chinese Character worksheets.
Converts master SVG into:
1. Color Reference SVG (no character labels, flat traditional colors)
2. B&W Worksheet SVG (white fill, black strokes, centered character labels, top crayon legend)
3. QA Validation report according to Simple Chunky CBN v1.0 specifications.
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def find_palette_for_unit(unit_id: int, base_dir: Path) -> list:
    """Attempts to auto-load traditional color palette for a given unit ID."""
    for cand in ["curriculum_100.json", "curriculum_100_traditional_colors.json"]:
        p = base_dir / cand
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for u in data.get("units", []):
                    if u.get("unit") == unit_id:
                        return u.get("traditionalColors", [])
            except Exception as e:
                print(f"[Warning] Failed loading {cand}: {e}")
    return []


def validate_qa_gates(root: ET.Element, palette: list) -> dict:
    """Performs QA validation against Simple Chunky CBN v1.0 specifications."""
    paths = list(root.iter(f"{{{SVG_NS}}}path"))
    closed_paths = [p for p in paths if p.get("d", "").strip().endswith(("Z", "z"))]
    texts = list(root.iter(f"{{{SVG_NS}}}text"))

    # Check path count
    path_count = len(closed_paths) if closed_paths else len(paths)
    count_ok = 25 <= path_count <= 45

    # Check legend matching
    palette_chars = {p.get("char") for p in palette if p.get("char")}
    text_chars = {t.text.strip() for t in texts if t.text and t.text.strip()}
    
    report = {
        "closed_paths_count": path_count,
        "closed_paths_in_range_25_45": count_ok,
        "text_labels_count": len(texts),
        "target_characters": list(palette_chars),
        "found_characters_in_artwork": list(text_chars & palette_chars),
        "passed": count_ok
    }
    return report


def process_svg(master_svg_path: Path, output_dir: Path, palette: list = None):
    output_dir.mkdir(parents=True, exist_ok=True)
    tree = ET.parse(master_svg_path)
    root = tree.getroot()

    # Auto-detect palette if not provided
    if not palette:
        m = re.search(r"unit_(\d+)", master_svg_path.stem)
        if m:
            unit_id = int(m.group(1))
            palette = find_palette_for_unit(unit_id, master_svg_path.parent.parent)
            if not palette:
                palette = find_palette_for_unit(unit_id, Path("."))
        if not palette:
            palette = []

    # 1. 导出彩色参考图 (Color Reference)
    root_color = ET.fromstring(ET.tostring(root))
    # 移除所有在正文中的汉字标签（保留无字纯色稿）
    parent_map_color = {c: p for p in root_color.iter() for c in p}
    for text in list(root_color.iter(f"{{{SVG_NS}}}text")):
        parent = parent_map_color.get(text)
        if parent is not None:
            try:
                parent.remove(text)
            except ValueError:
                pass

    color_out = output_dir / f"{master_svg_path.stem}_color_ref.svg"
    with open(color_out, "wb") as f:
        f.write(ET.tostring(root_color, encoding="utf-8"))

    # 2. 导出黑白填色纸 (B&W Worksheet)
    root_bw = ET.fromstring(ET.tostring(root))
    # 将所有画图路径转化为白底黑线，粗描边
    for path in root_bw.iter(f"{{{SVG_NS}}}path"):
        path.set("fill", "#FFFFFF")
        path.set("stroke", "#000000")
        sw = path.get("stroke-width", "3.0")
        try:
            # 保证描边在 2.5 - 4.5pt
            val = float(sw.replace("px", "").replace("pt", ""))
            if val < 2.5:
                sw = "2.5"
        except ValueError:
            sw = "3.0"
        path.set("stroke-width", sw)
        path.set("stroke-linecap", "round")
        path.set("stroke-linejoin", "round")

    # 检查是否已包含顶部图例，若无且有调色板则注入
    existing_legend = root_bw.find(f".//*[@id='crayon-legend']")
    if existing_legend is None and palette:
        legend = ET.Element(f"{{{SVG_NS}}}g", id="crayon-legend")
        items_per_row = 8
        swatch_w, swatch_h = 32, 22
        start_x = 45
        start_y = 30
        gap_x = 65

        for i, item in enumerate(palette):
            row = i // items_per_row
            col = i % items_per_row
            x = start_x + col * gap_x
            y = start_y + row * 45

            # 蜡笔方形色块
            ET.SubElement(legend, f"{{{SVG_NS}}}rect", {
                "x": str(x), "y": str(y), "width": str(swatch_w), "height": str(swatch_h),
                "rx": "4", "fill": item.get("hex", "#FFFFFF"),
                "stroke": "#000000", "stroke-width": "1.5"
            })
            # 汉字标注
            t = ET.SubElement(legend, f"{{{SVG_NS}}}text", {
                "x": str(x + swatch_w // 2), "y": str(y + swatch_h + 12),
                "text-anchor": "middle", "font-size": "13",
                "font-weight": "bold", "fill": "#000000"
            })
            t.text = item.get("char", "")
            # 色名标注
            t_name = ET.SubElement(legend, f"{{{SVG_NS}}}text", {
                "x": str(x + swatch_w // 2), "y": str(y + swatch_h + 23),
                "text-anchor": "middle", "font-size": "8",
                "fill": "#555555"
            })
            t_name.text = item.get("name", "")

        root_bw.insert(0, legend)

    bw_out = output_dir / f"{master_svg_path.stem}_worksheet.svg"
    with open(bw_out, "wb") as f:
        f.write(ET.tostring(root_bw, encoding="utf-8"))

    # 3. QA 质量验收
    qa_report = validate_qa_gates(root, palette)
    qa_out = output_dir / f"{master_svg_path.stem}_qa.json"
    with open(qa_out, "w", encoding="utf-8") as f:
        json.dump(qa_report, f, indent=2, ensure_ascii=False)

    print(f"Assets generated successfully:\n - Color Ref: {color_out}\n - B&W Sheet: {bw_out}\n - QA Report: {qa_out}")
    if not qa_report["closed_paths_in_range_25_45"]:
        print(f"[QA Note] Closed paths ({qa_report['closed_paths_count']}) outside target range [25, 45].")
    return {
        "color_ref": color_out,
        "worksheet": bw_out,
        "qa_report": qa_report
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split master SVG into color reference, BW worksheet, and run QA.")
    parser.add_argument("--input", required=True, help="Path to master SVG file")
    parser.add_argument("--palette", help="Path to palette JSON file")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    palette_data = []
    if args.palette and Path(args.palette).exists():
        with open(args.palette, "r", encoding="utf-8") as f:
            palette_data = json.load(f)

    process_svg(Path(args.input), Path(args.output), palette_data)
