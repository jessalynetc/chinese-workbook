# SOP: 生成中国传统色汉字填色页 (Color by Chinese Character)

## 1. 目标与定位
根据 `curriculum_100.json` 中的指定单元（如 Unit 1），批量生成符合“Simple Chunky CBN v1.0”规范的填色页：
1. 包含 25–45 个封闭大色块；
2. 外描边 4.5pt，内部描边 2.5pt，拐角与线端均为圆角；
3. 每个色块中心标注对应的汉字；
4. 顶部包含蜡笔图例栏（汉字 + 对应中国传统色色卡与色名）；
5. 自动衍生为：彩色完成图 (`_color_ref.svg`)、黑白填色线稿 (`_worksheet.svg`) 以及质量报告 (`_qa.json`)。

## 2. 输入
- 单元数据：`curriculum_100.json` (或 `curriculum_100_traditional_colors.json`)
- 脚本参数：`--unit [ID]` (1–12)

## 3. 执行工具与步骤
1. 调用 `python3 execution/gemini_generator.py --unit [ID] --mode coloring`
   - 向 Gemini 1.5 Pro/Flash 发送 `system_instruction_cbn.md` 提示词；
   - 依赖 `response_schema.json` 强类型约束；
   - 自动写入 `.tmp/unit_[ID]_master.svg`；
   - 自动触发 `execution/split_assets.py` 解析并输出到 `output/`。
2. 产物交付清单：
   - `output/unit_[ID]_master_color_ref.svg`：全彩完成参考图（移除正文文字标签，用于扫码伴读 H5 页面展示）；
   - `output/unit_[ID]_master_worksheet.svg`：黑白填色纸（白底黑线，正文汉字居中，顶部注入中国传统色蜡笔色卡）；
   - `output/unit_[ID]_master_qa.json`：色块数量、汉字覆盖率与安全边距质检报告。

## 4. 质量验收门禁 (QA Gates)
- [ ] 封闭路径数量在 25–45 之间 (`closed_paths_in_range_25_45 == true`)；
- [ ] 无面积小于 2% 画布的微小碎片色块；
- [ ] 每个色块中的文字没有压在轮廓线上；
- [ ] 顶部图例色名与 HEX 严格匹配中国传统色规范；
- [ ] QA 报告通过 (`passed == true`)。
