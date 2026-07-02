# Lettering Guide

Use this guide whenever the user chooses `带字版` or cares about the crooked childlike Chinese title. The title style is the main identity signal, so do not treat it as a normal font choice.

## Why Direct Generation Fails

Image models tend to turn "rough black handwritten Chinese" into a brush font: large, balanced, confident, and too clean. The reference lettering is different. It looks like an untrained person wrote display text with a blunt black marker, then accepted the mistakes.

The failure signs are:

- characters sit on an invisible grid;
- stroke thickness is too consistent;
- strokes have elegant tapering or calligraphic rhythm;
- each character looks like a standard typeface glyph with a rough texture added;
- four-character titles become a neat 2x2 table;
- the title and object compete instead of one clear title area and one quiet object anchor.

## First-Principles Lettering Model

The target title is not a texture applied to normal Chinese text. It has four separate control layers:

1. Semantic text: the exact characters the title must say.
2. Glyph skeleton: how each Chinese character is malformed, compressed, stretched, tilted, and spaced.
3. Stroke surface: black marker edges, blunt caps, broken joins, uneven pressure, and ink bumps.
4. Poster placement: loose vertical columns, off-grid title block, and white space around the title.

Most all-in-one image prompts can influence only layers 3 and 4. They usually keep a standard font skeleton underneath, so the result still feels like a font. When the user says the type is not restored enough, solve layer 2 directly with glyph and stroke references, not with more adjectives.

Use this control order:

1. lock the poster base without any generated title;
2. build a title construction reference sheet from `lettering/title-blocks`, `lettering/glyphs`, and `lettering/strokes`;
3. generate or draw the black title layer by looking at that sheet;
4. composite the accepted title layer onto the poster base.

## Target Lettering Anatomy

The desired title is not a font. It is a set of badly controlled black marker marks.

Use these traits:

- flat black ink, blunt marker feel, not dry-brush calligraphy;
- independent stroke pieces, with small gaps, overlaps, and ugly joins;
- uneven character scale: one character can be 15 percent larger or smaller than its neighbor;
- crooked verticals and non-parallel horizontals;
- irregular stroke pressure, but no elegant tapering;
- off-grid placement: characters drift left/right and do not share a baseline;
- awkward internal spaces: boxes, mouths, and radicals can be too large, too small, or slightly collapsed;
- naive construction: readable Chinese, but with childish proportions and imperfect stroke order;
- rough edge noise, broken ends, small ink bumps, and blunt caps.

Avoid:

- brush calligraphy, ink wash, elegant poster font, sans-serif, rounded cute handwriting, UI font, balanced commercial typography;
- perfect 2x2 title grids;
- shiny black texture, gray shading, gradients, embossed text, or vector-clean edges;
- adding pinyin, English, captions, labels, dates, numbers, or decorative text.

## Three-Part Typography Workflow

For publishable `带字版`, use separate assets instead of asking one image generation to solve everything.

Pass 1: poster base

- Preserve one real object as the photographic anchor.
- Remove busy surroundings and create a warm white field.
- Reserve a large empty title area in the upper-left or left side.
- Do not generate the title in this pass.
- Add at most one quiet micro-worker near the object if it helps the object story.

Pass 2: title construction reference sheet

- Build a model-facing private reference sheet with `scripts/build_title_reference_sheet.py` when local cutouts exist.
- Pass the exact target title to the script only so it can build the right number of off-grid layout boxes; keep the semantic text in the prompt. Include one to three `lettering/title-blocks` specimens, several `lettering/glyphs` specimens, and several `lettering/strokes` specimens.
- Use the sheet to show glyph skeleton defects: off-grid character boxes, non-parallel strokes, bad joins, blunt ends, uneven scale, and awkward internal spaces.
- Do not render the target title as a system font on the model-facing sheet. Keep exact semantic text in the prompt, and let the sheet control only layout pressure, bad spacing, and malformed stroke references.
- Do not treat the construction sheet as the final poster. It is a control image for the title layer.

Pass 3: title layer

- Generate or create only the black handwritten title on white or transparent background.
- Use the title construction reference sheet as the primary control reference.
- Iterate the title layer by itself until the handwriting works.
- Composite it onto the poster base without changing the object. Use `scripts/composite_title_layer.py` when working with local image files.

Direct all-in-one generation is allowed only for fast drafts. If the user complains that the type is not close enough, switch to the title construction sheet and title-layer workflow.

For maximum fidelity, use one of these title sources, in order:

1. a real hand-drawn title written by the user or designer and scanned/photo-cleaned;
2. a custom title asset drawn by tracing the private lettering references;
3. a title-only image-model generation guided by a construction reference sheet;
4. an all-in-one poster generation.

Treat options 3 and 4 as draft quality when exact resemblance matters. The reference style depends on malformed character skeletons, not just texture, so a normal generated Chinese glyph will usually remain too font-like.

## Building a Title Construction Sheet

When `private-assets/reference-cutouts/asset-index.json` exists, create a construction sheet before writing the title-layer prompt. The default sheet is for the image model: no English labels and no target characters drawn in a standard font.

```bash
python scripts/build_title_reference_sheet.py \
  --title "泰香开饭" \
  --out private-assets/reference-cutouts/title_reference_sheet_taixiang.png \
  --title-ref title_tiramisu_heavy_black \
  --title-ref title_salty_cheese_crooked
```

Use the output as a reference image for the title layer. The sheet is most useful when the requested title does not share characters with the references. It tells the model which defects to transfer: clumsy skeletons, broken joins, childlike spacing, and non-font rhythm.

Use `--human-labels` only when you need to inspect which assets were selected. Do not feed that labeled inspection sheet to an image model, because labels and standard-font target text can leak into the generated title.

If the generated title still looks like a font, keep the poster base and regenerate only the title layer with the same construction sheet. If the exact characters still fail, ask for or create a real handwritten title asset and composite it locally.

## Four-Character Title Layout

For four Chinese characters, do not make a neat square grid. Use two loose vertical columns:

```text
泰     开
香     饭
```

But the columns should be staggered:

- left column can start higher than right column;
- right column can lean inward or drift down;
- the lower characters should not align perfectly;
- column spacing can be slightly too tight or too loose;
- character boxes should feel hand-placed, not mechanically distributed.

When prompting, describe it as:

```text
two loose vertical handwritten columns, not a 2x2 table; left column contains "泰" above "香", right column contains "开" above "饭"; each character has a different size, tilt, x-position, and vertical gap
```

## Title-Layer Prompt Template

Use this when generating the title separately. If a title construction sheet exists, pass it as the main reference.

```text
Create a black handwritten Chinese title layer on a plain white background.

Text, exact:
[title]

Layout:
[layout description]

Style:
Use [title construction sheet path] as the primary reference. Match the glyph skeleton defects and stroke anatomy from the sheet. The title should look hand-written by an untrained child using a blunt black marker: flat black ink, crooked independent strokes, uneven character sizes, broken blunt stroke ends, awkward spacing, off-grid placement, bad joins, collapsed radicals, imperfect but readable Chinese. The characters should not sit on a perfect grid. No calligraphy, no brush font, no sans-serif font, no rounded cute handwriting, no elegant tapering, no clean font skeleton.

Output constraints:
Only the black title on white or transparent background. No object, no poster, no doodle figure, no logo, no extra text, no pinyin, no English, no numbers, no watermark.
```

## Poster-Base Prompt Template

Use this for Pass 1 of `带字版`.

```text
Create the typography-led poster base from the uploaded photo, but do not render the title yet.

Preserve [object] as a real photographic object with its original texture, color, shadow, and material. Remove the busy source background and place the object on a clean warm white poster field. Reserve a large empty title area in the upper-left or left side for a later black handwritten Chinese title layer. Keep the object smaller than the title area, usually lower-right or lower-middle, with enough white space around it.

Add at most one tiny primitive black-line micro-worker near the object, not in the title area. The worker should be functional, faceless, and hand-drawn, not cute.

No generated title, no captions, no logo, no watermark, no random text. If source object contains real printed text, keep it only if it is part of the photographed object and not visually dominant.
```

## Composition Corrections For Food Photos

Food-table photos usually start too busy. In `带字版`, do not keep the whole table scene.

Use this structure:

- choose one plate or one food basket, not the whole meal;
- object height: 30 percent to 42 percent of canvas;
- title block: 35 percent to 50 percent of canvas width and 30 percent to 45 percent of canvas height;
- title must have clean breathing room and should not touch the object;
- crop away competing plates, table texture, and decorative clutter unless one piece is the chosen object;
- if the plate rim has strong printed letters, keep them only inside the photographic object and prevent them from competing with the black title.

## Revision Prompts

## Local Compositing

After creating a poster base and a title-layer image, composite them locally:

```bash
python scripts/composite_title_layer.py \
  --base poster-base.png \
  --title title-layer.png \
  --out poster-final.jpg \
  --x 8% \
  --y 7% \
  --width 42%
```

Use a larger width for title-first posters and a smaller width when the object needs more room. The script thresholds dark pixels from the title layer, turns them into black ink, removes the white background, and places the result on the base.

If the title looks like a font:

```text
Regenerate only the title layer. Do not change the poster base. Use the title construction sheet more literally for glyph skeleton defects: off-grid character boxes, uneven character sizes, crooked independent strokes, ugly joins, blunt broken ends, non-parallel horizontals, collapsed radicals, no calligraphy rhythm, no clean font skeleton.
```

If the layout is too much like a menu photo:

```text
Regenerate only the poster base. Remove the table-scene feeling. Keep one real food object lower-right or lower-middle, reserve a large blank title field on the left, and reduce all other objects and decorative clutter.
```
