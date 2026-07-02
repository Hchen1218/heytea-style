---
name: heytea-doodle-poster
description: >-
  Turn an uploaded life photo into HEYTEA-inspired object-and-doodle poster
  concepts using two independent templates: a typography-led version with rough
  crooked childlike Chinese marker lettering, and a no-text narrative version
  driven by primitive black-line micro-worker actions. Use whenever the user asks
  for 喜茶简笔画海报, 歪歪扭扭儿童字, 儿童手绘风, 治愈饮品海报, 实物加小人涂鸦, or 白底手写字海报.
---

# Heytea Doodle Poster

Use this skill to turn a user's daily-life image into vertical poster concepts inspired by the playful HEYTEA product-poster language: real object anchors, white space, primitive black-line micro workers, and optionally rough crooked childlike Chinese marker lettering.

This is a style workflow, not an official HEYTEA asset generator. Do not add HEYTEA logos, official mascots, official packaging marks, or claims of brand affiliation unless the user supplies authorized assets and explicitly asks to use them.

## First steps

1. Confirm there is an input image. If the user did not provide one, ask for the image before generating.
2. Read `references/style-guide.md` before writing prompts or generating an image.
3. For `带字版`, also read `references/lettering-guide.md`. Do not rely on a single image-generation prompt to both render the final poster and solve exact Chinese handwriting.
4. If `private-assets/reference-cutouts/asset-index.json` exists, inspect it before prompt writing. Use these cutouts only as style/template references; do not claim they are official assets and do not add HEYTEA logos. Treat any record with `quality: avoid-default` or `copyright_scope: private-study-only` as analysis-only unless the user explicitly asks for a private local study. Do not package or publish raw source caches or extraction scripts.
5. Inspect the image and identify:
   - the one real object to preserve as the anchor;
   - the emotional hook or playful action suggested by that object;
   - one short crooked title candidate for the typography-led version;
   - one action story for the no-text narrative version.
6. Choose the generation template before generating:
   - `带字版`: typography is the first visual priority.
   - `无字版`: object-and-action story is the first visual priority, with no text anywhere.
   - `两套都出（推荐）`: generate two independent concepts using separate compositions and prompts.
   If the user has not chosen and wants immediate output, default to `两套都出（推荐）` and say that both templates are intentionally different.
7. Select references by template:
   - `带字版`: choose one primary `lettering/title-blocks/*` asset for title rhythm, two to six `lettering/glyphs/*` or `lettering/strokes/*` assets for glyph anatomy, plus zero or one quiet `figures/full-poses/*` asset if it supports the object.
   - `无字版`: choose one primary `figures/full-poses/*` action asset and optionally one `figures/action-parts/*` asset. Do not use lettering references.
   - `两套都出（推荐）`: choose separate reference sets for each version; never reuse the same composition with text toggled.
8. For `带字版`, default to a three-part workflow:
   - Pass 1: generate a clean poster base with the real object, white field, optional micro worker, and an intentionally empty title area.
   - Pass 2: build a model-facing title construction reference sheet with `scripts/build_title_reference_sheet.py` when reference cutouts exist. Keep the exact target text in the prompt; the sheet should not render target characters as a standard system font or include English labels unless `--human-labels` is explicitly used for inspection.
   - Pass 3: generate or place a separate black handwritten title layer using the construction sheet as the reference.
   If a title image layer is available, composite it onto the base with `scripts/composite_title_layer.py`. If a tool cannot composite layers, return both prompts and explain that direct in-image Chinese text is a draft-only shortcut.
9. If the image-generation tool can edit or use multiple reference images, generate from the uploaded user image plus the selected cutout references. If not, return the prompt packet with the selected asset paths and a short description of what each reference contributes.

## Default output

Produce the selected poster concept first, then include a compact prompt packet. For `两套都出（推荐）`, produce two concepts: one `带字版` and one `无字版`.

Use this response shape:

```markdown
## 成品
[image or output file path]

## 可编辑文案
- 主标题：...
- 模板：带字版 / 无字版 / 两套都出

## 生成 Prompt
- 带字版底图：...
- 带字版标题参考板：...
- 带字版标题层：...
- 无字版：...

## 使用素材
- 带字版：...
- 无字版：...

## 修正 Prompt
...
```

If no image tool is available, omit `## 成品` and start with `## 生成 Prompt`.

## Core style rules

- Keep one real photographed object as the visual anchor. Do not turn the whole image into a cartoon.
- Place the object on a clean white or soft off-white background with generous empty space.
- Add primitive black-line micro workers that interact with the object: pouring, carrying, tasting, climbing, cleaning, exploring, lifting, throwing, dragging, or repairing.
- For the typography-led template, make rough crooked childlike Chinese marker lettering the main style signal.
- For the no-text narrative template, forbid all text, letters, numbers, labels, and random glyphs.
- When reference cutout assets are available, use them to anchor line weight, wobble, figure proportions, and action pose. Use lettering cutouts as typography style references, not as final copied words, unless the user explicitly asks for a private local study mockup.
- Treat direct model-rendered Chinese text as exploratory. For publishable `带字版`, use a separate title construction sheet and title layer so the glyph skeleton can be iterated without changing the photographed object.
- Prefer 3:4 or 2:3 portrait output; default to `1024x1536` when the image tool supports explicit size.
- Avoid polished vector illustration, cute sticker style, comic panels, gradients, dense decoration, and realistic human faces.

## When the source image is difficult

- If the background is busy, crop or isolate the main object into white space before adding doodles.
- If there are several objects, choose the one with the clearest silhouette and strongest emotional association.
- If text rendering is unreliable in `带字版`, do not keep retrying a full-poster prompt. Switch to a blank poster base plus a title construction reference sheet and separate title layer. For highest fidelity, use a real handwritten title image or custom lettering asset, then composite it locally.
- If the user wants an image-model-only draft, still provide a title-layer prompt so the title can be regenerated without changing the object.
- If the first result is too cartoonish, revise by saying: preserve the real photographed object and change only the black doodle overlays.

## Evaluation

Use `references/evaluation.md` to review outputs. For this subjective visual skill, human comparison is more important than rigid numeric assertions.
