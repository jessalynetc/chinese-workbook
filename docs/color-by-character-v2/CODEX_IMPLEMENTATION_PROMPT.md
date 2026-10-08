# Codex Implementation Prompt — Upgrade Existing SOP to v2

You are modifying an EXISTING color-by-Chinese-character worksheet project. Do not start a new unrelated implementation or overwrite working artifacts. Read [`SOP_v2.md`](SOP_v2.md), [`SKILL.md`](../../skills/color-by-character/SKILL.md), and all prompts in [`skills/color-by-character/prompts/`](../../skills/color-by-character/prompts/) first.

## Inspect before modifying
1. Discover actual repository structure and read `curriculum_100.json` / `curriculum_100_traditional_colors.json`, `execution/gemini_generator.py`, `system_instruction_cbn.md`, `response_schema.json`, `execution/split_assets.py` if present.
2. Identify where Gemini currently creates isolated regions directly. Report exact root cause, current input/output contracts, SVG assumptions and APIs in use.
3. Report a small migration plan before code changes; avoid blind edits.

## Required refactor
- Replace single-shot "character list → region SVG" with 4 intermediate contracts: `curriculum_normalized.json`, `scene_plan.json`, `illustration_master.svg`, `segmented_master.svg` + `regions.json`.
- Build separate invocations/prompt templates for Stage 1 planning, Stage 2 scene drawing, Stage 3 segmentation, Stage 4 mapping.
- Retain the CLI interface if feasible: `python3 execution/gemini_generator.py --unit <ID> --mode coloring` but route it through the new stage orchestrator. Expose `--stop-after <stage>` and `--resume` if practical.
- Create stage-specific JSON schemas rather than forcing all tasks through one legacy `response_schema.json`. Ensure schemas match actual code.
- Upgrade `execution/split_assets.py` to derive answer/reference and worksheet from a **single canonical SVG geometry**; add path identity/geometry checks.
- Implement programmatic checks for visible closed regions, overlaps, gaps, area, text-fitting, palette, and printable margins. Where robust detection is not yet available, label checks explicitly unimplemented/needs_review (never fake PASS).
- Render preview PNGs and require visual inspection before declaring composition approved; automated similarity checks alone cannot prove coherence.
- Preserve original sample and output for before/after comparison; do not assume image-generation models consistently return valid editable SVG.
- Minimize unrelated changes; document prerequisites and usage.

## Test first
Select the nature landscape unit containing `山 水 木 石 土 火 田 金` (confirm actual unit ID in curriculum; never assume it is Unit 1). Generate only ONE test page and show:
1. scene plan
2. unlabeled continuous illustration preview
3. segmented preview
4. full-color reference
5. black/white Hanzi worksheet
6. honest QA metrics and blockers

**Acceptance**: mountain range and riverbank form coherent scene; tree trunks meet ground; fields and stones integrate into environment; all generated regions follow natural boundaries; no scattered fan/rectangle/circle vocabulary icons. A page with 30 disconnected shapes FAILS, even if 25–45 region count, palette, and text collision metrics pass.

## Deliverable report
List files changed; implementation commands; which QA rules actually run; previews produced; unresolved limitations; exact next corrective step. Do not claim production readiness without demonstrated pass for geometry and visually inspected output.
