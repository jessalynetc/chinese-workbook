"""
Gemini Generator: Deterministic orchestration script to generate Coloring Book & Workbook activity pages
using Google AI Studio (Gemini 1.5 Pro/Flash) or offline deterministic mock synthesis.

Adheres strictly to the 3-layer architecture:
- Reads system instructions from system_instruction_cbn.md / system_instruction_wb.md
- Reads response schema from response_schema.json
- Reads curriculum and traditional colors from curriculum_100.json
- Outputs master SVG to .tmp/ and splits into deliverables via split_assets.py
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Ensure project root is in sys.path for deterministic script imports
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Attempt to load requests
try:
    import requests
except ImportError:
    requests = None


def load_env_api_key() -> str:
    """Reads GEMINI_API_KEY from .env or OS environment."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val != "your_gemini_api_key_here":
                        key = val
                        break
    return key


def get_unit_data(unit_id: int) -> dict:
    """Retrieves unit data from curriculum_100.json or fallback."""
    for cand in ["curriculum_100.json", "curriculum_100_traditional_colors.json"]:
        p = Path(cand)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            for u in data.get("units", []):
                if u.get("unit") == unit_id:
                    return u
    raise ValueError(f"Unit {unit_id} not found in curriculum data.")


def generate_mock_cbn_svg(unit_id: int) -> str:
    """
    Deterministic synthesis of Simple Chunky CBN v1.0 SVG meeting:
    - US Letter (viewBox 0 0 612 792)
    - 28-36 closed chunky regions with rounded caps & joins
    - Centered Chinese characters from the unit palette
    - Traditional color fills
    - Safe margins and top crayon legend
    """
    unit_data = get_unit_data(unit_id)
    colors = unit_data.get("traditionalColors", [])
    theme = unit_data.get("theme", "自然天地")
    subject = unit_data.get("subject", "传统图景")

    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 612 792" width="612pt" height="792pt">',
        '  <defs>',
        '    <style>',
        '      .stroke-outer { stroke: #000000; stroke-width: 4.5; stroke-linecap: round; stroke-linejoin: round; }',
        '      .stroke-inner { stroke: #000000; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }',
        '      .char-label { font-family: "PingFang SC", "Kaiti SC", "SimSun", sans-serif; font-size: 16px; font-weight: bold; fill: #000000; }',
        '    </style>',
        '  </defs>',
        '  <!-- Background Canvas -->',
        '  <rect width="612" height="792" fill="#FFFFFF"/>',
        f'  <!-- Header: Unit {unit_id} {theme} - {subject} -->',
        f'  <text x="306" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#222222">《中华传统色·汉字密码涂色》第{unit_id}单元：{theme}</text>',
    ]

    # Generate 32 closed chunky puzzle blocks inside safe artwork boundaries (x: 45..567, y: 100..740)
    grid_cols = 4
    grid_rows = 8
    cell_w = 125
    cell_h = 75
    start_x = 55
    start_y = 100

    idx = 0
    for r in range(grid_rows):
        for c in range(grid_cols):
            x = start_x + c * cell_w
            y = start_y + r * cell_h
            color_item = colors[idx % len(colors)]
            char = color_item.get("char", "字")
            fill_hex = color_item.get("hex", "#FFFFFF")

            # Create chunky organic rounded path
            path_d = (
                f"M {x+10} {y} "
                f"Q {x+cell_w//2} {y+5} {x+cell_w-10} {y} "
                f"Q {x+cell_w} {y+cell_h//2} {x+cell_w-5} {y+cell_h-10} "
                f"Q {x+cell_w//2} {y+cell_h+5} {x+10} {y+cell_h} "
                f"Q {x-5} {y+cell_h//2} {x+10} {y} Z"
            )
            stroke_cls = "stroke-outer" if (r == 0 or r == grid_rows-1 or c == 0 or c == grid_cols-1) else "stroke-inner"
            sw = "4.5" if "outer" in stroke_cls else "2.5"

            svg_parts.append(f'  <g id="region_{idx+1}">')
            svg_parts.append(f'    <path d="{path_d}" fill="{fill_hex}" stroke="#000000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
            svg_parts.append(f'    <text x="{x + cell_w//2}" y="{y + cell_h//2 + 5}" text-anchor="middle" dominant-baseline="central" class="char-label">{char}</text>')
            svg_parts.append('  </g>')
            idx += 1

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generate_mock_workbook_svg(char: str, activity_type: str) -> str:
    """
    Deterministic synthesis of Amazon KDP compliant B&W Workbook activities:
    - wb_metaphor: 象形探秘
    - wb_maze: 汉字寻宝与迷宫
    - wb_tracing: 笔顺大闯关
    - wb_matching: 字形辨析
    """
    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 612 792" width="612pt" height="792pt">',
        '  <rect width="612" height="792" fill="#FFFFFF"/>',
        '  <!-- Print boundary guide safe box (margin 40pt) -->',
        '  <rect x="40" y="36" width="532" height="720" fill="none" stroke="#EEEEEE" stroke-width="1"/>'
    ]

    if activity_type == "tracing":
        svg_parts.extend([
            f'  <text x="306" y="70" text-anchor="middle" font-size="22" font-weight="bold">【汉字笔顺大闯关】核心字：{char}</text>',
            '  <text x="306" y="96" text-anchor="middle" font-size="13" fill="#666666">请用手指或蜡笔按照数字①②③的顺序描红，探索笔画轨迹！</text>',
            f'  <!-- Main Large Tracing Glyph -->',
            f'  <rect x="156" y="140" width="300" height="300" rx="16" fill="#FBFBFB" stroke="#000000" stroke-width="3"/>',
            f'  <line x1="156" y1="290" x2="456" y2="290" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="6,4"/>',
            f'  <line x1="306" y1="140" x2="306" y2="440" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="6,4"/>',
            f'  <text x="306" y="330" text-anchor="middle" font-size="190" font-weight="bold" fill="none" stroke="#222222" stroke-width="4" stroke-dasharray="10,6">{char}</text>',
            f'  <!-- Tracing Order Badges -->',
            f'  <circle cx="210" cy="200" r="16" fill="#000000"/>',
            f'  <text x="210" y="206" text-anchor="middle" font-size="14" fill="#FFFFFF" font-weight="bold">①</text>',
            f'  <circle cx="306" cy="180" r="16" fill="#000000"/>',
            f'  <text x="306" y="186" text-anchor="middle" font-size="14" fill="#FFFFFF" font-weight="bold">②</text>',
            f'  <!-- Small Practice Boxes below -->',
            '  <g id="practice-boxes">'
        ])
        for i in range(4):
            bx = 80 + i * 115
            svg_parts.append(f'    <rect x="{bx}" y="490" width="100" height="100" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>')
            svg_parts.append(f'    <line x1="{bx}" y1="{540}" x2="{bx+100}" y2="{540}" stroke="#E0E0E0" stroke-width="1" stroke-dasharray="4,4"/>')
            svg_parts.append(f'    <line x1="{bx+50}" y1="{490}" x2="{bx+50}" y2="{590}" stroke="#E0E0E0" stroke-width="1" stroke-dasharray="4,4"/>')
            svg_parts.append(f'    <text x="{bx+50}" y="{560}" text-anchor="middle" font-size="64" fill="none" stroke="#AAAAAA" stroke-width="2" stroke-dasharray="5,4">{char}</text>')
        svg_parts.extend([
            '  </g>',
            '  <text x="306" y="650" text-anchor="middle" font-size="16" font-weight="bold">自我挑战闯关星： ⭐ ⭐ ⭐</text>'
        ])
    elif activity_type == "maze":
        svg_parts.extend([
            f'  <text x="306" y="70" text-anchor="middle" font-size="22" font-weight="bold">【汉字寻宝迷宫】找到所有的“{char}”字！</text>',
            f'  <text x="306" y="96" text-anchor="middle" font-size="13" fill="#666666">从起点 🚩 沿着带有“{char}”字的方块连接出一条通往宝箱 🏁 的道路！</text>',
            '  <!-- Maze Grid 5x5 -->',
            '  <g id="maze-grid">'
        ])
        grid_items = [
            [char, "大", "小", "日", "月"],
            [char, char, "山", "石", "木"],
            ["水", char, char, "火", "土"],
            ["天", "地", char, char, "星"],
            ["云", "风", "雨", char, char]
        ]
        for r, row in enumerate(grid_items):
            for c, cell_char in enumerate(row):
                gx = 136 + c * 70
                gy = 150 + r * 70
                is_target = (cell_char == char)
                stroke_w = "3" if is_target else "1.5"
                svg_parts.append(f'    <rect x="{gx}" y="{gy}" width="65" height="65" rx="8" fill="#FFFFFF" stroke="#000000" stroke-width="{stroke_w}"/>')
                svg_parts.append(f'    <text x="{gx+32}" y="{gy+42}" text-anchor="middle" font-size="28" font-weight="bold" fill="#000000">{cell_char}</text>')
        svg_parts.extend([
            '  </g>',
            '  <text x="90" y="190" font-size="16" font-weight="bold">起点 🚩</text>',
            '  <text x="495" y="470" font-size="16" font-weight="bold">终点 🏁</text>',
            '  <text x="306" y="580" text-anchor="middle" font-size="15" fill="#333333">数一数：你一共踩过了几个目标汉字？ [      ] 个</text>'
        ])
    else:  # metaphor / default
        svg_parts.extend([
            f'  <text x="306" y="70" text-anchor="middle" font-size="22" font-weight="bold">【象形探秘】汉字从画里走出来：“{char}”</text>',
            '  <text x="306" y="96" text-anchor="middle" font-size="13" fill="#666666">古人观察大自然创造了象形字，看看它是怎么演变的！</text>',
            '  <!-- 3 Stages Progression -->',
            '  <rect x="70" y="150" width="130" height="150" rx="12" fill="#F9F9F9" stroke="#000000" stroke-width="2"/>',
            '  <text x="135" y="180" text-anchor="middle" font-size="14" fill="#666666">第1步：自然实物</text>',
            '  <circle cx="135" cy="230" r="35" fill="none" stroke="#000000" stroke-width="4"/>',
            '  <text x="135" y="325" text-anchor="middle" font-size="14" font-weight="bold">具象图画</text>',

            '  <text x="225" y="235" text-anchor="middle" font-size="28" font-weight="bold">➔</text>',

            '  <rect x="250" y="150" width="130" height="150" rx="12" fill="#F9F9F9" stroke="#000000" stroke-width="2"/>',
            '  <text x="315" y="180" text-anchor="middle" font-size="14" fill="#666666">第2步：甲骨金文</text>',
            f'  <text x="315" y="245" text-anchor="middle" font-size="52" font-weight="bold">{char}</text>',
            '  <text x="315" y="325" text-anchor="middle" font-size="14" font-weight="bold">古代汉字</text>',

            '  <text x="405" y="235" text-anchor="middle" font-size="28" font-weight="bold">➔</text>',

            '  <rect x="430" y="150" width="130" height="150" rx="12" fill="#FFFFFF" stroke="#000000" stroke-width="3"/>',
            '  <text x="495" y="180" text-anchor="middle" font-size="14" fill="#666666">第3步：现代楷体</text>',
            f'  <text x="495" y="245" text-anchor="middle" font-size="64" font-weight="bold" fill="#000000">{char}</text>',
            '  <text x="495" y="325" text-anchor="middle" font-size="14" font-weight="bold">今日汉字</text>',

            '  <!-- Interactive Exercise -->',
            '  <rect x="70" y="370" width="490" height="260" rx="16" fill="#FAFAFA" stroke="#000000" stroke-width="2.5"/>',
            f'  <text x="315" y="410" text-anchor="middle" font-size="17" font-weight="bold">【小小观察家】找找看！画面中藏着什么规律？</text>',
            f'  <text x="100" y="460" font-size="14" fill="#333333">1. “{char}”的字形骨架就像我们生活中的哪一样东西？</text>',
            '  <rect x="100" y="480" width="430" height="40" rx="6" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5"/>',
            f'  <text x="100" y="550" font-size="14" fill="#333333">2. 动手画一画：你能用“{char}”字画一幅可爱的小画吗？</text>',
            '  <rect x="100" y="570" width="430" height="50" rx="6" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5"/>'
        ])

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def call_gemini_api(api_key: str, system_prompt: str, user_prompt: str, schema: dict) -> dict:
    """Calls Google AI Studio Gemini API with structured output."""
    if not requests:
        raise RuntimeError("Python requests library is required for live API calls.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": schema,
            "temperature": 0.4
        }
    }
    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    candidate = result["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(candidate)


def main():
    parser = argparse.ArgumentParser(description="Generate Coloring Pages and Workbook Activities using Gemini or Deterministic Engine.")
    parser.add_argument("--mode", choices=["coloring", "workbook"], default="coloring", help="Generation mode")
    parser.add_argument("--unit", type=int, help="Unit ID (1-12) for coloring mode")
    parser.add_argument("--char", type=str, help="Target Chinese character for workbook mode")
    parser.add_argument("--type", choices=["maze", "tracing", "metaphor", "matching"], default="metaphor", help="Activity type for workbook mode")
    parser.add_argument("--mock", action="store_true", help="Force deterministic mock generator without making API calls")
    parser.add_argument("--output-dir", default="output", help="Directory to save generated deliverables")
    args = parser.parse_args()

    api_key = load_env_api_key()
    tmp_dir = Path(".tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "coloring":
        if not args.unit:
            print("[Error] --unit is required for coloring mode (e.g. --unit 1)")
            sys.exit(1)

        unit_id = args.unit
        master_svg_path = tmp_dir / f"unit_{unit_id}_master.svg"
        print(f"[Orchestration] Generating Unit {unit_id} Color-by-Chinese-Character page...")

        if args.mock or not api_key:
            if not api_key:
                print("[Info] No active GEMINI_API_KEY detected in .env. Running deterministic offline generator.")
            svg_content = generate_mock_cbn_svg(unit_id)
        else:
            print("[Info] Active GEMINI_API_KEY detected. Dispatching request to Gemini 1.5 API...")
            sys_prompt = Path("system_instruction_cbn.md").read_text(encoding="utf-8")
            with open("response_schema.json", "r", encoding="utf-8") as f:
                schema = json.load(f)
            unit_data = get_unit_data(unit_id)
            user_prompt = f"Generate Simple Chunky CBN v1.0 master SVG for Unit {unit_id}: {json.dumps(unit_data, ensure_ascii=False)}"
            try:
                data = call_gemini_api(api_key, sys_prompt, user_prompt, schema)
                svg_content = data.get("masterSvg", "")
            except Exception as e:
                print(f"[Warning] API call failed ({e}). Falling back to deterministic offline synthesis.")
                svg_content = generate_mock_cbn_svg(unit_id)

        master_svg_path.write_text(svg_content, encoding="utf-8")
        print(f"[Success] Master SVG saved to: {master_svg_path}")

        # Automatically execute split_assets.py to generate deliverables and QA report
        from execution.split_assets import process_svg
        process_svg(master_svg_path, out_dir)

    elif args.mode == "workbook":
        target_char = args.char or "日"
        activity_type = args.type
        print(f"[Orchestration] Generating Workbook activity ({activity_type}) for character: {target_char}...")

        if args.mock or not api_key:
            svg_content = generate_mock_workbook_svg(target_char, activity_type)
        else:
            print("[Info] Dispatching request to Gemini 1.5 API for workbook generation...")
            sys_prompt = Path("system_instruction_wb.md").read_text(encoding="utf-8")
            with open("response_schema.json", "r", encoding="utf-8") as f:
                schema = json.load(f)
            user_prompt = f"Generate {activity_type} activity page for Chinese character: {target_char}"
            try:
                data = call_gemini_api(api_key, sys_prompt, user_prompt, schema)
                svg_content = data.get("masterSvg", "")
            except Exception as e:
                print(f"[Warning] API call failed ({e}). Falling back to deterministic offline synthesis.")
                svg_content = generate_mock_workbook_svg(target_char, activity_type)

        wb_dir = out_dir / "worksheets"
        wb_dir.mkdir(parents=True, exist_ok=True)
        wb_path = wb_dir / f"wb_{target_char}_{activity_type}.svg"
        wb_path.write_text(svg_content, encoding="utf-8")
        print(f"[Success] Workbook activity page saved to: {wb_path}")


if __name__ == "__main__":
    main()
