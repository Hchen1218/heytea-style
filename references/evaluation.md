# Evaluation Guide

Use this for human review and lightweight evals.

## Pass Criteria

An output is successful when:

- one real object from the input remains recognizable and photographic;
- the background is white or off-white with strong negative space;
- the chosen template is clear before generation: `带字版`, `无字版`, or `两套都出（推荐）`;
- if reference cutouts exist, selected assets are listed and match the chosen template;
- black primitive micro-worker lines interact with the object instead of floating randomly;
- the doodles feel naive, functional, and hand-drawn rather than cute or polished;
- the poster does not use official HEYTEA logos, official marks, or watermarks;
- the final image feels quiet, healing, playful, and publishable.

For `带字版`, success depends first on the lettering:

- a primary `lettering/title-blocks/*` cutout is used or listed as the title rhythm reference when reference assets are available;
- `lettering/glyphs/*` and `lettering/strokes/*` are used or recommended when the title looks too font-like;
- the workflow uses or recommends a separate poster-base pass, title construction reference sheet, and title-layer pass when publishable lettering is required;
- the title is a primary composition element, not a small caption;
- the Chinese characters have malformed glyph skeletons: rough, crooked, childlike, uneven, heavy black, off-grid, ugly joins, collapsed or oversized internal spaces, and not a font-like brush style;
- four-character titles use two loose staggered vertical columns, not a perfect 2x2 table;
- the object and micro worker support the title instead of competing with it.

For `无字版`, success depends first on action storytelling:

- a primary `figures/full-poses/*` cutout is used or listed as the action reference when reference assets are available;
- `figures/action-parts/*` is used or listed only when an action mark or prop helps the story;
- no `lettering/*` cutout is selected for this version;
- there is no invented text anywhere;
- the composition does not reserve a title block;
- the object and micro worker form a complete small action scene.

## Common Failure Modes

- Full cartoon conversion: the real object loses its photographic texture.
- Decorative clutter: too many doodles, stickers, bubbles, or props.
- Wrong brand behavior: the image invents official logos or fake packaging marks.
- Text noise: extra illegible Chinese or English appears in the image.
- Template confusion: the no-text version is just the typography version with the title removed.
- Asset mismatch: the no-text version uses lettering references, or the typography-led version ignores the available title-lettering references.
- Weak typography: the title looks like a clean font, neat handwriting, cute rounded text, elegant calligraphy, or a standard glyph skeleton with rough texture pasted on top.
- Missing glyph control: the response keeps adding adjectives instead of using a title construction reference sheet, glyph samples, and stroke samples.
- Single-pass trap: repeated all-in-one generations keep changing the object while trying to fix the title.
- Grid trap: the four-character title forms a polished square layout instead of loose staggered hand placement.
- Weak interaction: doodles are present but do not explain or play with the object.
- Cute-character drift: the micro worker becomes a mascot, chibi character, or expressive cartoon person.
- Over-designed look: vector icons, gradients, UI-card composition, or generic poster polish.

## Review Questions

Ask these after each generated poster:

1. Is the real object still the hero?
2. Which template was used, and is that template visually obvious?
3. Were the selected reference cutout assets appropriate for the template?
4. For `带字版`, was the title handled through a construction reference sheet and separate title layer?
5. For `带字版`, does the lettering have malformed childlike glyph skeletons rather than a clean font skeleton?
6. For `无字版`, does the action story work without any text?
7. Does the micro worker look functional and primitive rather than cute?
8. Is there enough white space?
9. What single revision would improve it most?

## Suggested Evals

For a formal skill-creator loop, compare with-skill and without-skill outputs on:

- object preservation;
- negative-space composition;
- template choice before generation;
- private reference asset selection when `asset-index.json` is available;
- difference between typography-led and no-text narrative layouts;
- use of a poster-base/title-construction-sheet/title-layer workflow for publishable typography-led outputs;
- crooked childlike lettering quality for `带字版`;
- absence of invented text for `无字版`;
- primitive micro-worker action quality;
- avoidance of official brand marks;
- usefulness of the prompt packet for iteration.

## Release Checks

Before committing or packaging this skill:

- no public file contains local absolute workstation paths, source social-media filenames, chat-temp paths, or generated image cache references;
- `private-assets/reference-cutouts/` may be included when reference images are intended to ship;
- raw source caches and extraction scripts are not present in the repository or `.skill` archive;
- `scripts/build_title_reference_sheet.py` and `scripts/composite_title_layer.py` are present in the package if the docs mention them;
- the title reference sheet used for image generation is model-facing: no English labels and no target title rendered in a standard system font;
- `git status --short` is reviewed before staging; do not stage `.DS_Store`, stale packages, or unrelated generated outputs.
