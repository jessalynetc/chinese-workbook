# Chinese Color-by-Character Skill — Markdown Prompt Pack v2.0

本目录提供**文档/提示词规范**（Reference Specification），用于指导 Color-by-Chinese-Character V2 流水线的设计与实施。

## 包含内容
- [`SOP_v2.md`](SOP_v2.md) — 完整设计规范与门禁说明（可执行操作版见 [`directives/color_by_character_v2.md`](../../directives/color_by_character_v2.md)）。
- [`SKILL.md`](../../skills/color-by-character/SKILL.md) — Codex / Antigravity Skill 入口，说明调用顺序及停止条件。
- [`01_semantic_planner.md`](../../skills/color-by-character/prompts/01_semantic_planner.md) — 先规划统一叙事场景。
- [`02_illustration_generator.md`](../../skills/color-by-character/prompts/02_illustration_generator.md) — 先创作无文字连贯插画。
- [`03_region_segmenter.md`](../../skills/color-by-character/prompts/03_region_segmenter.md) — 在原插画上自然切分，而不是拼装色块。
- [`04_character_palette_mapper.md`](../../skills/color-by-character/prompts/04_character_palette_mapper.md) — 最后分配汉字与核实过的中国传统色。
- [`05_qa_reviewer.md`](../../skills/color-by-character/prompts/05_qa_reviewer.md) — 程序几何 QA + 视觉构图 QA。
- [`CODEX_IMPLEMENTATION_PROMPT.md`](CODEX_IMPLEMENTATION_PROMPT.md) — 可复制给 AI 的实施要求。

## 使用
先阅读 [`CODEX_IMPLEMENTATION_PROMPT.md`](CODEX_IMPLEMENTATION_PROMPT.md)，检查你的仓库，提交变更计划，然后分阶段实施。先用自然主题 Unit 做**单页验证**，满意后再批量生成。

## 核心前后差异
旧：`curriculum → isolated shapes → labels`  
新：`curriculum → scene plan → coherent illustration → semantic segmentation → labels + palette → shared SVG derivatives → QA`

**视觉规范**：Simple Chunky CBN v1.1 / semantic continuity before region count。
