# SOP: 生成中国传统色汉字填色页 (Color by Chinese Character)

## 1. 目标与定位
根据 `curriculum_100_traditional_colors.json` 中的指定单元（如 Unit 1），批量生成符合“Simple Chunky CBN v1.0”规范的填色页：
1. 包含 25–45 个封闭大色块；
2. 外描边 4.5px，内部描边 2.5px，拐角为圆角；
3. 每个色块中心标注对应的汉字；
4. 顶部包含蜡笔图例栏（汉字 + 对应中国传统色色块）；
5. 自动衍生为：彩色完成图 (`_color_ref.svg`) 与 黑白填色线稿 (`_worksheet.svg`)。

## 2. 输入
- 单元数据：`unit`、`theme`、`subject`、`characters`、`traditionalColors`
- 脚本参数：`unit_id` (1–14)

## 3. 执行工具与步骤
1. 调用 `execution/gemini_generator.py --unit [ID] --mode coloring`
   - 向 Gemini 1.5 Pro 发送 System Prompt 与该单元参数；
   - 获取结构化输出包含的 `masterSvg`。
2. 调用 `execution/split_assets.py --input .tmp/unit_[ID]_master.svg`
   - 解析 SVG DOM 树；
   - 提取并导出 `output/unit_[ID]_color_ref.svg`；
   - 转换为白底黑线，注入顶部中国传统色图例，导出 `output/unit_[ID]_worksheet.svg`。

## 4. 质量验收门禁 (QA Gates)
- [ ] 封闭路径数量在 25–45 之间；
- [ ] 无面积小于 2% 画布的微小碎片色块；
- [ ] 每个色块中的文字没有压在轮廓线上；
- [ ] 顶部图例色名与 HEX 严格匹配中国传统色规范。
