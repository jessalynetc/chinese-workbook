# SOP: 生成汉字游戏练习册页面 (Workbook Activity Pages)

## 1. 目标
为 128 页儿童中文练习册生成游戏化页面（杜绝机械抄写）：
- 题型 A：象形演变与探秘（图画到汉字的具象化转化）
- 题型 B：汉字迷宫（按指定汉字或笔画路径走出迷宫）
- 题型 C：笔顺大描红（手指引导大号空心字）
- 题型 D：部首积木与形近字配对找茬

## 2. 页面尺寸与安全边距
- 格式：US Letter (8.5 × 11 英寸) 纵向；
- 打印安全边距：左右外边距至少 0.5 英寸，内侧装订线至少 0.75 英寸；
- 色彩模式：100% 纯黑白灰阶（高对比度，适合 KDP 打印）。

## 3. 执行流程
1. 读取 `curriculum_100_traditional_colors.json` 获取目标汉字；
2. 运行 `execution/gemini_generator.py --char [汉字] --type [maze|tracing|metaphor]`；
3. 输出为适合打印的矢量 SVG 并转换为 PDF。
