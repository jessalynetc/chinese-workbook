---
name: chinese-color-by-character
summary: Generate coherent children’s illustrated color-by-Chinese-character worksheets from curriculum units via a staged SVG pipeline.
---

# Chinese Color by Character Skill (v2)

Invoke for: "Generate unit N Chinese character coloring worksheet" / "为 Unit N 生成中国传统色汉字填色页".

## Primary command contract
`--unit N` from `curriculum_100.json` or `curriculum_100_traditional_colors.json`. The actual code entry point must be inspected before running; this documentation **does not claim scripts have been updated**.

## Required workflow
Read [color_by_character_v2.md](../../directives/color_by_character_v2.md) (or reference spec [SOP_v2.md](../../docs/color-by-character-v2/SOP_v2.md)), then run these in order:
1. `prompts/01_semantic_planner.md`
2. `prompts/02_illustration_generator.md`
3. `prompts/03_region_segmenter.md`
4. `prompts/04_character_palette_mapper.md`
5. deterministic renderer / parity checker
6. `prompts/05_qa_reviewer.md`

**Critical constraint:** The project must construct **an unlabeled coherent scene before any 25–45-region segmentation**. Never derive composition from isolated character-bearing shapes. Never separately redraw worksheet and reference artwork.

## Stop conditions
Stop after composition gate if unlabeled scene looks like a sticker/icon collage. Stop after region segmentation if visible connected regions have overlap/gaps or major silhouette changed. Stop before reporting success if independent geometry and visual checks unavailable.

## Integrations
Existing `execution/gemini_generator.py`, `system_instruction_cbn.md`, `response_schema.json`, `execution/split_assets.py` require refactoring per [color_by_character_v2.md](../../directives/color_by_character_v2.md); do not overwrite functional code blindly. Inspect repo before changes. Model name and API structured-output support must be checked against real SDK/environment.

## Output expectation
`output/unit_[ID]_master_color_ref.svg`, `output/unit_[ID]_master_worksheet.svg`, `output/unit_[ID]_master_qa.json` plus intermediates, evidence-based QA report. Reports MUST distinguish measured vs visually reviewed vs unverified claims.
