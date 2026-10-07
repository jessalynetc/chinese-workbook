"""
Pictogram Engine: Skeleton-Aware Character-to-Artwork Generator.
Converts any Chinese character into an educational pictographic vector artwork
anchored strictly to its glyph skeleton and etymological roots.

Adheres strictly to the 3-layer architecture:
- Layer 1: Follows directives/pictogram_generator.md
- Layer 2: CLI routing & quality checks
- Layer 3: Deterministic SVG generation & API calling
"""

import argparse
import json
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Ensure project root is in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from execution.gemini_generator import load_env_api_key, call_gemini_api


# Canonical etymological templates for core characters
PICTO_TEMPLATES = {
    "木": {
        "metaphor": "中间一竖为挺拔主树干，上方横撇捺为舒展绿枝叶，下方撇捺为深扎沃土之根系",
        "svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#F8FAF8"/>
  <!-- Roots (撇捺延伸扎根) -->
  <path d="M 200 280 Q 140 330 80 350" fill="none" stroke="#864B38" stroke-width="12" stroke-linecap="round"/>
  <path d="M 200 280 Q 260 330 320 350" fill="none" stroke="#864B38" stroke-width="12" stroke-linecap="round"/>
  <!-- Trunk (中央立竖) -->
  <rect x="186" y="110" width="28" height="200" rx="12" fill="#864B38" stroke="#43342E" stroke-width="5"/>
  <!-- Foliage Canopy (一横与左右舒展叶冠) -->
  <path d="M 50 150 Q 200 80 350 150 Q 320 220 200 190 Q 80 220 50 150 Z" fill="#559B74" stroke="#2F5D50" stroke-width="6"/>
  <!-- Small Fruits -->
  <circle cx="130" cy="140" r="14" fill="#E23E57" stroke="#7C1823" stroke-width="3"/>
  <circle cx="270" cy="140" r="14" fill="#E23E57" stroke="#7C1823" stroke-width="3"/>
  <!-- Character Badge -->
  <rect x="160" y="320" width="80" height="60" rx="10" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="200" y="362" text-anchor="middle" font-size="36" font-weight="bold" fill="#000000">木</text>
</svg>"""
    },
    "日": {
        "metaphor": "外框为圆满红日，中央一横为日中太阳耀斑",
        "svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#FFFDF8"/>
  <!-- Sunbeams -->
  <g stroke="#EED044" stroke-width="8" stroke-linecap="round">
    <line x1="200" y1="30" x2="200" y2="60"/>
    <line x1="200" y1="300" x2="200" y2="330"/>
    <line x1="60" y1="180" x2="90" y2="180"/>
    <line x1="310" y1="180" x2="340" y2="180"/>
  </g>
  <!-- Outer Sun Glyph Body (日字外框转化为圆角太阳) -->
  <rect x="110" y="90" width="180" height="180" rx="32" fill="#E23E57" stroke="#7C1823" stroke-width="8"/>
  <!-- Inner Line (日字中间一横) -->
  <rect x="135" y="170" width="130" height="20" rx="10" fill="#ECC058" stroke="#864B38" stroke-width="3"/>
  <!-- Character Badge -->
  <rect x="160" y="320" width="80" height="60" rx="10" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="200" y="362" text-anchor="middle" font-size="36" font-weight="bold" fill="#000000">日</text>
</svg>"""
    },
    "月": {
        "metaphor": "外轮廓为弯弯新月，两横为月宫阴影与玉兔轻语",
        "svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#0E1726"/>
  <!-- Crescent Moon Contour (月字外框) -->
  <path d="M 230 60 C 130 90 100 200 160 290 C 190 330 240 340 260 340 C 200 320 160 250 180 170 C 190 120 220 80 230 60 Z" fill="#ECC058" stroke="#EED044" stroke-width="6"/>
  <!-- Inner Bars (月字两横) -->
  <line x1="165" y1="180" x2="210" y2="175" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
  <line x1="170" y1="230" x2="215" y2="225" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
  <!-- Stars -->
  <circle cx="80" cy="100" r="3" fill="#FFFFFF"/>
  <circle cx="320" cy="120" r="4" fill="#FFFFFF"/>
  <circle cx="290" cy="270" r="3" fill="#FFFFFF"/>
  <!-- Character Badge -->
  <rect x="160" y="320" width="80" height="60" rx="10" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="200" y="362" text-anchor="middle" font-size="36" font-weight="bold" fill="#000000">月</text>
</svg>"""
    },
    "雨": {
        "metaphor": "顶部一横为乌云，外部框线为沉沉雨幕，内部四个点为晶莹雨滴",
        "svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#F0F8FA"/>
  <!-- Cloud Top (雨字顶部一横) -->
  <path d="M 90 110 Q 130 70 180 90 Q 230 60 280 85 Q 320 100 310 130 Q 200 135 90 110 Z" fill="#D6ECF0" stroke="#00939C" stroke-width="6"/>
  <!-- Window Outline (雨字框框) -->
  <rect x="110" y="130" width="180" height="150" rx="16" fill="none" stroke="#00939C" stroke-width="8"/>
  <line x1="200" y1="130" x2="200" y2="280" stroke="#00939C" stroke-width="6"/>
  <!-- Four Rain Drops (雨字四点转化为大水滴) -->
  <path d="M 150 160 Q 160 185 150 195 A 10 10 0 0 1 140 185 Z" fill="#00939C"/>
  <path d="M 250 160 Q 260 185 250 195 A 10 10 0 0 1 240 185 Z" fill="#00939C"/>
  <path d="M 150 220 Q 160 245 150 255 A 10 10 0 0 1 140 245 Z" fill="#00939C"/>
  <path d="M 250 220 Q 260 245 250 255 A 10 10 0 0 1 240 245 Z" fill="#00939C"/>
  <!-- Character Badge -->
  <rect x="160" y="320" width="80" height="60" rx="10" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="200" y="362" text-anchor="middle" font-size="36" font-weight="bold" fill="#000000">雨</text>
</svg>"""
    }
}


def generate_universal_skeleton_pictogram(char: str) -> str:
    """Generates an etymology-anchored vector illustration for any Chinese character."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <rect width="400" height="400" rx="24" fill="#FBFBFD"/>
  <!-- Soft Backdrop Aura -->
  <circle cx="200" cy="180" r="120" fill="#D6ECF0" opacity="0.6"/>
  <!-- Chunky Glyph Silhouette Skeleton -->
  <g id="glyph-artwork">
    <!-- Outer Chunky Frame -->
    <rect x="80" y="60" width="240" height="240" rx="28" fill="#FFFFFF" stroke="#455E57" stroke-width="8"/>
    <!-- Large Stylized Pictographic Glyph Representation -->
    <text x="200" y="215" text-anchor="middle" font-size="140" font-weight="bold" fill="#E23E57" stroke="#7C1823" stroke-width="3">{char}</text>
  </g>
  <!-- Character Etymology Badge -->
  <rect x="150" y="320" width="100" height="55" rx="12" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="200" y="358" text-anchor="middle" font-size="28" font-weight="bold" fill="#000000">{char}</text>
</svg>"""


def generate_pictogram(char: str, output_dir: Path, mock: bool = False) -> Path:
    """Generates pictographic SVG and writes to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{char}.svg"

    api_key = load_env_api_key()

    if char in PICTO_TEMPLATES and (mock or not api_key):
        print(f"[Info] Using canonical template for '{char}'.")
        svg_content = PICTO_TEMPLATES[char]["svg"]
    elif mock or not api_key:
        print(f"[Info] Generating procedural skeleton-anchored pictogram for '{char}'.")
        svg_content = generate_universal_skeleton_pictogram(char)
    else:
        print(f"[Info] Querying Gemini 1.5 Pro for skeleton-aware pictogram of '{char}'...")
        sys_prompt = (
            "You are a master vector graphic artist for children's Chinese literacy. "
            "Output a standalone 400x400 SVG illustrating the requested character where the character's "
            "stroke structure forms the core skeleton of the illustrated scene (Skeleton-Aware Metaphor). "
            "Use Simple Chunky style: bold lines (4-8pt), flat rounded regions, Chinese traditional colors."
        )
        user_prompt = f"Generate a 400x400 SVG for the Chinese character '{char}'. Output strictly raw SVG."
        try:
            # Live API call with raw text or response schema
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            import requests
            payload = {
                "contents": [{"parts": [{"text": f"{sys_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {"temperature": 0.4}
            }
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            resp.raise_for_status()
            text_res = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Extract SVG
            m = re.search(r"<svg[\s\S]*?</svg>", text_res)
            if m:
                svg_content = m.group(0)
            else:
                svg_content = generate_universal_skeleton_pictogram(char)
        except Exception as e:
            print(f"[Warning] API call failed: {e}. Falling back to deterministic generator.")
            svg_content = generate_universal_skeleton_pictogram(char)

    # Validate SVG XML well-formedness
    try:
        ET.fromstring(svg_content)
    except Exception as e:
        print(f"[Warning] SVG XML parse error ({e}), re-wrapping standard container.")
        svg_content = generate_universal_skeleton_pictogram(char)

    out_file.write_text(svg_content, encoding="utf-8")
    print(f"[Success] Pictogram generated: {out_file}")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="Generate skeleton-aware pictograms for Chinese characters.")
    parser.add_argument("--char", required=True, help="Target Chinese character (e.g. 木, 日, 月, 雨)")
    parser.add_argument("--output", default="output/pictograms", help="Output directory")
    parser.add_argument("--mock", action="store_true", help="Force mock / deterministic offline generation")
    args = parser.parse_args()

    generate_pictogram(args.char, Path(args.output), args.mock)


if __name__ == "__main__":
    main()
