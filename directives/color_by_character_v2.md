# SOP v2.0 — 中国传统色汉字填色页 (Operational SOP)

> **Document Status**: **Authoritative Operational SOP** for the V2 Color-by-Chinese-Character pipeline.  
> **Reference Specification**: [docs/color-by-character-v2/SOP_v2.md](../docs/color-by-character-v2/SOP_v2.md)  
> **Associated Skill**: [skills/color-by-character/SKILL.md](../skills/color-by-character/SKILL.md)  
> **Prompts Location**: [skills/color-by-character/prompts/](../skills/color-by-character/prompts/)  
> **Implementation Status**: Staged / Documentation only. Pipeline implementation pending approval.


## 目标
根据 `curriculum_100.json`（或 `curriculum_100_traditional_colors.json`）指定单元制作一幅**先作为完整插画成立**、再作为 Color by Chinese Character (CBCC) 练习页成立的儿童填色作品。

**不允许**从汉字直接拼贴孤立色块。固定流程：

`curriculum → semantic scene plan → unlabeled coherent illustration → region segmentation → character/palette assignment → one canonical vector master → two derivatives → QA`

## 设计优先级
1. **Semantic continuity before region count**：整页是一幅连贯的风景/故事，不是散开的教学图标。
2. **Illustration first**：即使移除汉字，也能识别主体、前中后景和主题。
3. **Segment existing shapes**：优先利用山脊、河岸、树冠、田埂、石头、衣服等自然边界，必要时才少量内部切分。
4. **Single source of geometry**：彩色答案和黑白练习页复用完全相同的封闭区域几何。
5. **Legible Chinese labeling**：汉字放入清晰可写色块，不能与边界重叠。

## 输入与运行
- 课程文件：`curriculum_100.json`，允许使用替代文件 `curriculum_100_traditional_colors.json`。
- 必填：`--unit <ID>`（当前支持 1–12，具体以课程数据为准）。
- 可选：`--difficulty easy_plus`、`--page-size us_letter`、`--seed <n>`、`--dry-run`。
- 目标：Simple Chunky CBN v1.1；默认 25–45 个**可着色的最终连通区域**，5–8 种颜色（以单元映射为先，不要强迫不匹配的字符/颜色）。
- 印刷：US Letter portrait，可配置 A4；页面安全边距至少 0.4 in；外部重要轮廓约 4.5 pt、内部约 2.5 pt（需按实际 SVG 单位换算），round join/cap；汉字字号根据可用内接空间调节，不能小到无法阅读。

## 阶段与门禁

### Stage 0 — Curriculum normalization
读取指定单元，提取：字、词义、可能对应的场景对象、官方传统色名/HEX、必备词汇与可选词汇。未知或互相矛盾的字段明确记录，不得编造课程内容。

输出：`.tmp/unit_[ID]_curriculum_normalized.json`。Gate 0：每个教学汉字均可追溯到源数据。

### Stage 1 — Semantic scene planning
调用 `../skills/color-by-character/prompts/01_semantic_planner.md`；**先构思画面**，例如山水自然主题为连贯山脉、河流、树林、石头、田野。不能因需用到“金”“火”等字而画不合理的漂浮图形；如果某字缺乏自然对应物，采用合理叙事元素并标记需要编辑确认。

输出：`.tmp/unit_[ID]_scene_plan.json`。Gate 1：主体、前中后景、空间关系清晰；逐字覆盖且语义成立；删除所有文字后仍是一幅完整的儿童插画。

### Stage 2 — Illustration first
调用 `../skills/color-by-character/prompts/02_illustration_generator.md`，根据 scene plan 生成**没有汉字/数字/图例**的连贯 flat-vector 儿童插画。构图完整，主体突出；SVG 可含自然对象组，但不可为了凑数量直接拼 25–45 块。

输出：`.tmp/unit_[ID]_illustration_master.svg`、`_illustration_preview.png`（若渲染环境可用）。Gate 2：视觉检查通过（人工或视觉模型审核），不存在漂浮拼图感、物件缺乏空间关系、符号化排列。

### Stage 3 — Semantic segmentation
调用 `../skills/color-by-character/prompts/03_region_segmenter.md`。维持主轮廓与整体构图，按自然边界 → 语义子部分 → 少量适度人工内切分的顺序切割。交叠对象必须确定前后层及**最终可见**区域边界；不得靠重叠 SVG 路径假装完成无缝分割。

输出：`.tmp/unit_[ID]_segmented_master.svg`、`.tmp/unit_[ID]_regions.json`、`_segmentation_preview.png`。Gate 3：25–45 个最终封闭、互不重叠的可见着色区（不含文字和图例）；共同拼成连贯场景；每区具 parentObjectId，且位置足够放字。无法兼顾完整画面与数量时先保住构图，进入人工审查，而非强行切割。

### Stage 4 — Character and color mapping
调用 `../skills/color-by-character/prompts/04_character_palette_mapper.md`。依据对象语义映射汉字；同字可以出现在多个区块。按照课程指定传统色映射色号/HEX：若数据没有“每个汉字对应唯一颜色”规则，则**要求明确采用哪种教学模式**，不要臆造。所有区域须指定有效汉字和 palette ID。labelPoint 是实际多边形内部的视觉安全点，不能盲用 centroid。

输出：`.tmp/unit_[ID]_mapped_master.svg`、`.tmp/unit_[ID]_region_assignments.json`、`.tmp/unit_[ID]_palette.json`。Gate 4：所有必教汉字至少出现一次；所有 label 在对应 region 内，无碰线；色彩数/色卡与课程一致。

### Stage 5 — Deterministic derivative rendering
统一几何来自 mapped canonical SVG/regions；由程序确定性产生：
- `output/unit_[ID]_master_color_ref.svg`：同一色块几何，正确填色，无正文汉字（用于参考答案/扫码展示）。
- `output/unit_[ID]_master_worksheet.svg`：相同几何，白色填充、黑色线条、正文汉字标签；顶部加入蜡笔样式图例（汉字、传统色名与颜色 swatch）。
- 可选对应 PNG/PDF 预览；不要让生成模型分别重画两个版本。

Gate 5：通过 path identity / canonical geometry hash 对照，确认两个版本完全一致（只允许 fill、label、legend 与页面呈现不同）。

### Stage 6 — QA review
调用 `../skills/color-by-character/prompts/05_qa_reviewer.md` 配合程序校验。输出 `output/unit_[ID]_master_qa.json` 和 `output/unit_[ID]_qa_review.md`。**数值 QA 不能替代视觉 QA**。视觉规则需要实际渲染复核；无法验证时标记 `needs_review`，不得报告 `passed: true`。

## QA 规则（v2）
| 类别 | 检查 | 标准 |
|---|---|---|
| Curriculum | 源数据可追溯 | 每字有 source |
| Composition | 完整、连贯、移除标签可辨识 | 人工/视觉审核通过 |
| Semantic grouping | 每个最终着色区具有 parent object | 100% |
| Final visible geometry | 封闭、非重叠、无意外空洞 | 0 critical |
| Complexity | 最终区域数量 | 默认 25–45；偏离则 review |
| Region size | <0.4% 的面积 | 默认 fail，必要小细节须手动批准或合并 |
| Region size | 0.4–1.0% 面积 | warning；按 print readability 判断 |
| Label | 标签完整包含在本区且有笔画余量 | 100% |
| Palette | 色名 HEX、编号、汉字映射 | 课程规则一致 |
| Parity | 彩色/黑白的 region paths | 100% 一致 |
| Print | 页面边距、字、线宽、图例 | 可印刷且清晰 |

**注意**：`shared_boundary_ratio` 可以诊断碎片感，但不宜以“每个 path 都需要共享边界”当硬规则，因为太阳、鸟、岩石等可以天然独立。若统计，请定义为「可见区域中与其他区域共享边界的数量占比」，不包括页面背景；建议先记录不强制阈值。`floating_region_ratio` 同理需语义审查，不能仅由不相接判错。

## 失败恢复
- Scene incoherent → 返回 Stage 1/2，重写场景或构图；**不要**在 Stage 3 修补拼图。
- Too many micro regions → Stage 3 合并/简化局部；保留父对象外轮廓。
- Region overlap / gap → 修正真实平面分割几何，不可只遮盖视觉缺陷。
- Label collision → 在同一区另找最大内接空间或合并/放大区块。
- Invalid palette/character → 返回 Stage 4，对照 curriculum 修正，禁止随意替代。
- Failed visual review → 阻止最终 `passed`，输出需人工复核项。

每个阶段最多自动重试 2 次；仍不满足则保存中间产物并停止，防止无穷循环。

## 与现有代码的迁移
现有入口 `python3 execution/gemini_generator.py --unit [ID] --mode coloring` 可以保留为 orchestration wrapper，但需从单次 Gemini→SVG 改为逐阶段调用；`system_instruction_cbn.md` 拆为 prompts/01–04；`response_schema.json` 建议拆成 scene_plan / illustration_metadata / segmentation / mapping 的多个 schema。`execution/split_assets.py` 保留并升级为确定性 renderer + geometry parity validator。不要假设 Gemini 1.5 Pro/Flash 始终可用；API 模型及结构化输出支持应由实际环境配置验证。

## 完整交付
`scene_plan.json`, `illustration_master.svg`, `segmented_master.svg`, `regions.json`, `palette.json`, `region_assignments.json`, `mapped_master.svg`, `_color_ref.svg`, `_worksheet.svg`, `_qa.json`, `_qa_review.md`。若前置阶段不通过，只交付草稿和阻断原因，勿伪称可出版。
