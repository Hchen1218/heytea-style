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

## Desktop-Pet Pass Criteria

A desktop-pet request succeeds only when the staged workflow is visible in the response:

- no visual generation starts without an input image;
- no-subject inputs ask for a clearer photo instead of inventing a character;
- multi-subject inputs present numbered choices instead of silently selecting one;
- a container and its contents are treated as one subject by default;
- the candidate board contains three versions of the same source identity and palette in one identical neutral stance and ground anchor;
- candidates differ through face system, short-limb proportions, structural crookedness, and stable temperament—not action poses;
- pose-only boards are explicitly consolidated into one neutral canonical master instead of forcing a meaningless selection;
- every candidate has the intended limb inventory; by default exactly two arms and two clearly visible legs, even when strokes contain deliberate gaps;
- the user explicitly approves a candidate before motion generation;
- all twelve required actions are present and share one stable identity;
- when optional `fall` and `touch` are present, their line/color language matches the newest approved v2 action family and their transition frames connect `drag → fall → land` and `walk → touch → walk` without a visible redesign;
- the user explicitly approves the contact sheet and looping preview before packaging;
- review images may use white, but runtime strips have transparent corners and no white rectangle;
- the result includes a validated schema-v2 ZIP or honestly states which artifacts remain unbuilt.
- the non-technical delivery folder contains only the validated pack, preview, usage note, and platform start/quit entrypoints; it does not duplicate the Electron runtime.

Desktop-pet visual quality passes when:

- the photographed subject remains recognizable after full illustration conversion;
- the subject itself is the character body;
- one to three source colors, hesitant thin-to-medium pen structure, minimal face, and short limbs remain consistent;
- drinks and soft foods use deliberate media zoning—light colored pencil, broad childlike wax crayon, paper-white clear areas, and only optional pale smears—rather than one uniform texture, oil-paint mass, smooth gradient, or flat digital fill;
- every long structural or limb stroke visibly meanders; no ruler-straight segment survives merely because the overall object is asymmetric;
- object geometry is structurally asymmetric and hand-redrawn rather than a clean repeated template with a wobble filter;
- when two-pass construction is used, the color pass preserves every accepted skeleton stroke, gap, face, limb, and position instead of redrawing a cleaner outline;
- cuteness is carried by proportion, material marks, and readable action rather than a generic large-eyed face;
- actions read clearly at the 120–140 px default size;
- feet share a stable ground anchor and loops do not jump;
- `signature` expresses the subject instead of adding a generic animation;
- no official logos, mascots, random text, costume, glossy 3D treatment, or polished sticker outline appears.

Desktop-pet pack quality passes when both build and independent validation succeed. The validator must reject missing actions, unsafe paths, incorrect strip dimensions, fully opaque assets, non-transparent corners, empty frames, invalid hitboxes, and mismatched ZIP roots.

## Desktop-Pet Failure Modes

- **Gate skipping**: motion is generated before character approval, or packaging begins before motion approval.
- **Silent subject choice**: one item is selected from a multi-object photo without asking.
- **Identity drift**: face, outline, palette, or appendages change between actions.
- **Poster leakage**: photographic texture or micro-worker poster composition is reused as the pet body.
- **Candidate theater**: three candidates are merely recolors or depict different source subjects.
- **Pose theater**: waving, leaning, walking, or another action is presented as an identity-design difference; without the pose, the candidates are effectively identical.
- **Missing canonical master**: pose-only sketches are accepted, but no neutral identity lock is created before the twelve actions.
- **Broken-line amputation**: a deliberate contour gap is misread as permission to omit a leg or arm, leaving candidates with inconsistent limb counts.
- **Generic cartoon substitution**: a uniform thick outline, smooth gradient, sticker border, or generic chibi face replaces the mixed-media line and color grammar.
- **Material flattening**: every region receives the same crayon/pencil texture instead of distinct dry media selected by material.
- **Oil-paint overcorrection**: broad wet-looking smears, gouache masses, or oil-pastel rubbing replace the original colored-pencil and childlike crayon vocabulary.
- **Straight-segment collage**: the object is assembled from broken lines, but each individual wall, rim, limb, or facial mark remains ruler-straight.
- **Surface-only wobble**: the outline wiggles, but the rim, walls, lid, base, and perspective remain mechanically clean and symmetrical.
- **Color-pass repair**: the black-only skeleton is suitably broken, but coloring reconnects gaps, regularizes curves, or replaces it with a polished outline.
- **White-box runtime**: review background is baked into animation strips.
- **Partial white-box runtime**: a generated floor line encloses a pale patch inside one frame even though the four strip corners remain transparent.
- **Cross-frame spill**: an arm, leg, color block, or motion dash crosses a generated cell boundary and appears as a detached side mark in the neighboring runtime frame.
- **Unreadably fast gesture**: four to six key drawings are played at high FPS, so the complete action disappears in under a second.
- **Generic action set**: `signature` is another wave or jump unrelated to the object.
- **Unbounded cursor behavior**: the pet continuously follows the cursor, travels farther than one short episode, fails to return to its origin, or captures input.
- **Drop teleport**: releasing above the floor snaps the window to ground before the falling pose can be seen.
- **Unverified delivery**: a prompt, contact sheet, or unchecked directory is described as a validated importable pack.
- **Per-pet runtime duplication**: every role folder carries another Electron application, `node_modules`, or build output instead of addressing the one installed runner.
- **Hard-kill close button**: the close entrypoint terminates a process forcefully instead of sending the runner's graceful `--quit` command.

## Desktop-Pet Review Questions

1. Was subject ambiguity resolved before generation?
2. Which must-preserve features identify the source object?
3. Are the three candidates genuinely the same character?
4. Is there explicit approval for the selected character?
5. Are all twelve states present, readable, and consistently anchored?
6. Is there explicit approval for the motion preview?
7. Are runtime strips transparent and structurally valid?
8. Did both the builder and validator succeed?
9. Does the imported runner remain usable without blocking normal desktop input?

## Release Checks

Before committing or packaging this skill:

- no public file contains local absolute workstation paths, source social-media filenames, chat-temp paths, or generated image cache references;
- `private-assets/reference-cutouts/` may be included when reference images are intended to ship;
- raw source caches and extraction scripts are not present in the repository or `.skill` archive;
- `scripts/build_title_reference_sheet.py` and `scripts/composite_title_layer.py` are present in the package if the docs mention them;
- `scripts/build_desktop_pet_pack.py` and `scripts/validate_desktop_pet_pack.py` are present when desktop-pet packaging is documented;
- the Electron runtime contains source and tests but no `node_modules`, `dist`, imported user packs, or app-data state;
- Python pack tests and Electron core tests pass;
- the title reference sheet used for image generation is model-facing: no English labels and no target title rendered in a standard system font;
- `git status --short` is reviewed before staging; do not stage `.DS_Store`, stale packages, or unrelated generated outputs.
