# SOP: 生成汉字游戏练习册页面 (Workbook Activity Pages)

## 1. 目标
为 128 页儿童中文练习册生成游戏化页面（杜绝机械抄写）：
- 题型 A：象形演变与探秘（图画到汉字的具象化转化，参数 `--type metaphor`）
- 题型 B：汉字寻宝与迷宫（按指定汉字或笔画路径走出迷宫，参数 `--type maze`）
- 题型 C：笔顺大描红（手指引导大号空心字，参数 `--type tracing`）
- 题型 D：部首积木与形近字配对找茬（参数 `--type matching`）

## 2. 页面尺寸与安全边距
- 格式：US Letter (8.5 × 11 英寸) 纵向 (`viewBox="0 0 612 792"`)；
- 打印安全边距：左右外边距至少 36pt (0.5 英寸)，内侧装订线至少 45pt；
- 色彩模式：100% 纯黑白灰阶（高对比度，适合 Amazon KDP 印刷）。

## 3. 执行流程
1. 读取 `curriculum_100.json` 获取目标汉字；
2. 运行 `python3 execution/gemini_generator.py --char [汉字] --mode workbook --type [maze|tracing|metaphor|matching]`；
3. 输出结果保存于 `output/worksheets/wb_[汉字]_[type].svg`。

## 4. 质量验收门禁 (QA Gates)
- [ ] 页面尺寸符合 US Letter (612 × 792 pt)；
- [ ] 笔画与指引清晰，包含清晰标题与双语提示；
- [ ] 迷宫有明确起点与终点，且目标汉字路径可连通；
- [ ] 描红字包含笔顺序号圆标（①②③）。
