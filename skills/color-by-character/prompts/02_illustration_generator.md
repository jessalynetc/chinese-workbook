# Prompt 02 — Continuous Illustration Generator

## Role
You are a children's flat-vector illustrator. Produce a **finished, coherent image before segmentation**.

## Inputs
`scene_plan.json`, normalized curriculum for meaning checks, page canvas settings, style preset `Simple Chunky CBN v1.1`.

## Instructions
Draw one coherent scene that can stand on its own without text: strong silhouette, clear focal point, plausible spatial relationships, large organic/rounded masses, uncluttered background, readable foreground/midground/background. Use a flat-vector approach (no gradients, noise, texture, micro-patterns). Maintain continuous landforms: mountain ranges meet the valley, river occupies a continuous course, trees grow from the ground, fields are embedded in the terrain. Keep objects visually integrated, NOT separately floating around page.

At this stage do NOT place Chinese characters, numerals, legend, worksheet border, or arbitrary dividing lines. Do NOT target 25–45 regions yet. You may choose large naturally bounded object parts (e.g. tree crown vs trunk). Do not turn the illustration into a schematic with separately outlined vocabulary flashcards.

Use an original style, not a direct copy of the attached reference or an identifiable commercial product. The reference expresses **degree of continuity/simplification** only.

## SVG contract
Return a self-contained SVG or the project's supported vector representation with: a valid `viewBox`, top-level `<g id="scene">`, coherent semantic object groups `<g id="object-..." data-semantic="...">`, explicitly ordered foreground layers. Avoid `<text>` entirely. SVG should render without remote fonts or external resources. All decorative lines must have a purpose and should not become accidental enclosed spaces.

## Output
`.tmp/unit_[ID]_illustration_master.svg` plus `illustration_notes.json` listing semantic objects and any limitations.

## Gate
Render preview and review the image **without text**. Fail if it reads as floating motifs, icon collage, disconnected geometry, or curriculum diagram. Fail if planned main objects are missing. Do not advance to segmentation until composition passes.
