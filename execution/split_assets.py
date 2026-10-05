"""
Deterministic asset splitter and validator for Color by Chinese Character worksheets.
Converts master SVG into:
1. Color Reference SVG (no character labels, flat traditional colors)
2. B&W Worksheet SVG (white fill, black strokes, centered character labels, top crayon legend)
"""

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

def process_svg(master_svg_path: Path, output_dir: Path, palette: list):
    output_dir.mkdir(parents=True, exist_ok=True)
    tree = ET.parse(master_svg_path)
    root = tree.getroot()

    # 1. 导出彩色参考图
    root_color = ET.fromstring(ET.tostring(root))
    # 移除文字标签
    for text in list(root_color.iter(f"{{{SVG_NS}}}text")):
        parent = root_color.find(f".//{{{SVG_NS}}}text/..")
        if parent is not None:
            try:
                parent.remove(text)
            except ValueError:
                pass

    color_out = output_dir / f"{master_svg_path.stem}_color_ref.svg"
    with open(color_out, "wb") as f:
        f.write(ET.tostring(root_color, encoding="utf-8"))

    # 2. 导出黑白填色纸
    root_bw = ET.fromstring(ET.tostring(root))
    for path in root_bw.iter(f"{{{SVG_NS}}}path"):
        path.set("fill", "#FFFFFF")
        path.set("stroke", "#000000")
        path.set("stroke-width", path.get("stroke-width", "3.0"))

    # 添加顶部图例
    legend = ET.Element(f"{{{SVG_NS}}}g", id="crayon-legend")
    for i, item in enumerate(palette):
        x = 40 + (i % 8) * 68
        y = 25 + (i // 8) * 50
        # 矩形色卡
        ET.SubElement(legend, f"{{{SVG_NS}}}rect", {
            "x": str(x), "y": str(y), "width": "24", "height": "24",
            "rx": "4", "fill": item.get("hex", "#FFFFFF"),
            "stroke": "#000000", "stroke-width": "1.5"
        })
        # 汉字标注
        t = ET.SubElement(legend, f"{{{SVG_NS}}}text", {
            "x": str(x + 12), "y": str(y + 38),
            "text-anchor": "middle", "font-size": "14",
            "font-weight": "bold", "fill": "#000000"
        })
        t.text = item.get("char", "")
        # 色名标注
        t_name = ET.SubElement(legend, f"{{{SVG_NS}}}text", {
            "x": str(x + 12), "y": str(y + 50),
            "text-anchor": "middle", "font-size": "9",
            "fill": "#555555"
        })
        t_name.text = item.get("name", "")

    root_bw.insert(0, legend)
    bw_out = output_dir / f"{master_svg_path.stem}_worksheet.svg"
    with open(bw_out, "wb") as f:
        f.write(ET.tostring(root_bw, encoding="utf-8"))

    print(f"Assets generated successfully:\n - {color_out}\n - {bw_out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split master SVG into color reference and BW worksheet.")
    parser.add_argument("--input", required=True, help="Path to master SVG file")
    parser.add_argument("--palette", help="Path to palette JSON file")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    palette_data = []
    if args.palette and Path(args.palette).exists():
        with open(args.palette, "r", encoding="utf-8") as f:
            palette_data = json.load(f)

    process_svg(Path(args.input), Path(args.output), palette_data)
