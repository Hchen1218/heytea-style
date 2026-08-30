# Evaluation Guide

Use this for human review and lightweight evals.

## Photo-Entry Pass Criteria

When a usable photo arrives without an explicit output request, the response offers exactly:

1. 生成带字版海报
2. 生成不带字海报
3. 生成一张风味小怪兽

At this entry gate, nothing is generated and no runner preflight or installation discussion appears. An already explicit text-poster, no-text-poster, both-posters, flavor-monster, or source-faithful request bypasses redundant choices.

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

## Approved-Monster Fusion-Poster Pass Criteria

A fusion poster succeeds only after explicit approval of a canonical `flavor-monster` identity:

- the original product remains photographic and preserves its silhouette, proportions, structure, materials, and defining regions;
- the approved monster preserves its body topology and proportions, face layout, exactly two arms and two legs, attachment points, palette, dry-media treatment, and flavor-DNA marks;
- only the monster pose changes, and one clear interaction verb creates readable contact or cause-and-effect with the product;
- irrelevant background props are removed when they compete with the subject;
- a text version uses a purpose-built base, title construction sheet, and separate title layer;
- a no-text version contains no words, letters, numbers, captions, labels, pseudo-glyphs, signatures, or watermarks and does not reserve a title block;
- when both are requested, the two versions use independent compositions rather than one base with text toggled;
- runner availability never gates this static poster output.

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
- Premature runner gate: a static monster or fusion poster triggers environment preflight or installation discussion.
- Unapproved fusion: a monster is placed into a poster before the user explicitly approves its canonical identity.
- Product drift: fusion-poster generation redraws, cartoonizes, or structurally changes the photographed product.
- Fusion identity drift: the approved monster's body, face, 2+2 limbs, palette, material, or flavor marks change while adapting its pose.
- Runtime coupling: a missing or declined runner blocks an approved static fusion-poster branch.

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
- if the user did not already choose one, the response asks whether to make a 写实卡通桌宠 or 风味小怪兽桌宠 before generating candidates;
- the chosen character mode is recorded and remains fixed through character and motion approval;
- `source-faithful` uses a three-candidate board with the same source identity, palette, neutral stance, and ground anchor; candidates differ through face system, short-limb proportions, structural crookedness, and stable temperament—not action poses;
- `flavor-monster` defaults to one best complete-color identity master; multiple identity directions appear only when the user explicitly asks to explore;
- pose-only multi-image boards are explicitly consolidated into one neutral canonical master instead of forcing a meaningless selection;
- every identity has the declared appendage inventory; `source-faithful` defaults to exactly two arms and two clearly visible legs, while every `flavor-monster` has exactly two separate open black-line arms and two separate open black-line legs;
- the user explicitly approves the candidate or single identity master before motion generation;
- environment preflight occurs only after canonical identity approval and explicit selection of a runnable desktop pet, and it resolves before motion generation;
- when fusion poster and runnable pet are both selected, runner failure blocks only motion and packaging while the static poster continues;
- source-faithful schema-v2 packs contain all twelve required actions with one stable identity; optional `fall` and `touch` connect `drag → fall → land` and `walk → touch → walk` without redesign;
- flavor-monster schema-v3 packs contain 6–10 reachable behaviors, complete bindings, explicit phase exits, and persistent `sleep-enter → sleeping-loop → wake-exit` behavior;
- the user explicitly approves the contact sheet and looping preview before packaging;
- review images may use white, but runtime strips have transparent corners and no white rectangle;
- the result includes an independently validated mode-appropriate ZIP (v2 for source-faithful, v3 for flavor-monster) or honestly states which artifacts remain unbuilt.
- the non-technical delivery folder contains only the validated pack, preview, usage note, and platform start/quit entrypoints; it does not duplicate the Electron runtime.

Shared desktop-pet visual quality passes when:

- one to three source colors and the mode-appropriate hesitant thin-to-medium pen structure remain consistent; `flavor-monster` concentrates black linework in its sparse face, two arms, two legs, and partial marks rather than a complete body frame;
- drinks and soft foods use deliberate media zoning—long loose lightly layered colored-pencil sweeps, a few broad open wax-crayon arcs or separated blocks, paper-white clear areas, and only optional pale smears—rather than one equal-density texture, oil-paint mass, smooth gradient, or flat digital fill;
- every long structural or limb stroke visibly meanders and varies pressure or thickness within the same mark; no ruler-straight segment, smooth constant-width Bézier curve, or clean vector path with superficial jitter passes merely because the overall object is asymmetric;
- object geometry is structurally asymmetric and hand-redrawn rather than a clean repeated template with a wobble filter;
- when two-pass construction is used, the color pass preserves every accepted skeleton stroke, gap, face, limb, and position instead of redrawing a cleaner outline;
- cuteness is carried by proportion, material marks, and readable action rather than a generic large-eyed face;
- actions read clearly at the 120–140 px default size;
- feet share a stable ground anchor and loops do not jump;
- `signature` expresses the subject instead of adding a generic animation;
- no official logos, mascots, random text, costume, glossy 3D treatment, or polished sticker outline appears.

`source-faithful` visual quality also requires:

- the photographed subject remains recognizable after full illustration conversion;
- the subject itself is the character body;
- the outer silhouette, major internal divisions, and must-preserve object/container features remain stable across candidates and actions;
- the output does not silently turn into an animal, mascot, or flavor monster.

`flavor-monster` visual quality also requires:

- the first impression is a cute, friendly, independent flat doodle creature rather than a literal source object, an unpleasant organic form, or a conventionally completed mascot;
- an internal identity brief maps no more than three source signals into a source-derived body topology, dry-media fields, abstract marks, restrained irregularities, or regional media and records motion verbs separately for later behavior design;
- the brief declares body silhouette and center of gravity; a region-by-region plan for pencil, crayon, active internal paper-white, and occasional faded edges; exactly two arms and two legs with black-line attachment points, lengths, proportions, and resting pose; facial-mark count, placement, black-line shape, friendly emotion, full-length meander, and within-stroke pressure or thickness variation; a cuteness test; a stable floor anchor; and literal source structures that must disappear;
- source recognition in the static identity comes from at least two kinds of visual DNA chosen from color, ingredient, and material rather than a replaceable palette alone; motion DNA is evaluated later;
- the body is a soft, compact, friendly dry-media color mass without a complete black enclosing outline or a complete pizza slice, mushroom, cup, container, ingredient, or other literal source-object silhouette;
- every identity has exactly two separate open black-line arms and two separate open black-line legs whose strokes meander and change pressure or thickness internally; no limb is colored, volumetric, missing, merged into the body, constant-width, mechanically smooth, or replaced by a tendril or trailing body material;
- every facial mark is a sparse, friendly, readable black doodle line with visible hand variation; one or two eyes, offset layouts, and no conventional mouth are allowed, while colored features, realistic or shaded eyes, large chibi eyes, complex facial anatomy, smooth Bézier curves, and constant-width monoline fail;
- `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png` controls only HEYTEA-like cuteness, handmade awkwardness, and the relationship between an unoutlined body and black doodle face/limbs; the photo controls body topology, and copying the example's silhouette, protrusion placement, face layout, or proportions fails;
- the dry-media and thin-stroke boards have separate material and black-line roles, while the action board is deferred to motion, smudged structure is repair-only, and the mixed-media-object failure board is never a positive input;
- fleshy collapse, exposed or realistic tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, or any disturbing organic reading fails the cuteness gate even when source DNA is recognizable;
- the full-resolution identity visibly contains irregular paper-white inside the body, distinct mark behavior between major color zones, and incomplete or faded selected edges; fine paper grain beneath edge-to-edge saturated color does not qualify;
- the 120–140 px reduction preserves deliberate internal paper-white rather than compression noise, keeps major color zones coherent rather than speckled, and retains the source-derived body, friendly black-line face, two black-line arms, two black-line legs, at least two visual-DNA kinds, and stable ground anchor;
- the approved body, black-line face, fixed 2+2 black-line limbs, flavor-DNA marks, and anchor remain stable across actions;
- behavior interpretation uses the monster's approved graphic features, larger episode arcs, and explicit enter/loop/exit phases rather than preserving the v2 state names.

Desktop-pet pack quality passes when both build and independent validation succeed. The validator must reject missing v2 actions or v3 bindings, unreachable behaviors, non-terminating loops, illegal completion events, unsafe paths, incorrect strip dimensions, fully opaque assets, non-transparent corners, empty frames, invalid hitboxes, and mismatched ZIP roots.

## Desktop-Pet Failure Modes

- **Gate skipping**: a fusion poster or motion is generated before character approval, motion begins before the environment gate reports `ready`, or packaging begins before motion approval.
- **Premature environment gate**: runner preflight occurs before canonical identity approval or merely because the user asks for a static monster.
- **Static-output runtime coupling**: a missing runner prevents an approved monster fusion poster from continuing.
- **Missing mode gate**: candidate generation starts from an unspecified “桌宠” request without asking 写实卡通 or 风味小怪兽.
- **Silent mode inference**: food or drink is automatically routed to one character mode without the user choosing it.
- **Cross-mode leakage**: `source-faithful` becomes a generic monster, or `flavor-monster` retains a complete source container body.
- **Silent subject choice**: one item is selected from a multi-object photo without asking.
- **Identity drift**: face, outline, palette, or appendages change between actions.
- **Poster leakage**: photographic texture or micro-worker poster composition is reused as the pet body.
- **Candidate theater**: a `source-faithful` board's three candidates are merely recolors or depict different source subjects, or a `flavor-monster` workflow produces unsolicited alternatives instead of one resolved concept.
- **Pose theater**: waving, leaning, walking, or another action is presented as an identity-design difference; without the pose, multiple images are effectively identical.
- **Missing canonical master**: pose-only sketches are accepted, but no neutral identity lock is created before the twelve actions.
- **Broken-line amputation**: a deliberate contour gap is misread as permission to omit a leg or arm, leaving candidates with inconsistent limb counts.
- **Generic cartoon substitution**: a uniform thick outline, smooth gradient, sticker border, or generic chibi face replaces the mixed-media line and color grammar.
- **Body black-frame substitution**: the body receives a complete black enclosing outline instead of remaining a dry-media color mass.
- **Limb-grammar failure**: an arm or leg is colored, volumetric, missing, merged into the body, or replaced by a tendril, trailing flesh, paw, mitten, foot, toe cluster, or realistic joint instead of one of the required 2+2 open black doodle strokes.
- **Face-grammar failure**: facial features are colored, realistic, shaded, chibi-large, anatomically complex, or otherwise not sparse friendly black doodle lines.
- **Literal source anatomy**: a complete pizza slice, mushroom, cup, container, ingredient, or recognizable food organ survives instead of being semantically abstracted.
- **Grotesque monster substitution**: fleshy collapse, exposed tissue, slime, horror tendrils, corpse-like sagging, sharp anatomy, or another disturbing organic reading replaces cute friendliness.
- **Reference-role leakage**: the public pink-green example supplies the new silhouette, protrusion placement, face layout, or proportions instead of only cuteness and the unoutlined-body/black-line-feature relationship.
- **Material flattening**: every region receives the same crayon/pencil texture instead of distinct dry media selected by material.
- **Pseudo-handmade full fill**: paper grain, uniform digital speckle, dense tiny strokes or loops, or crosshatching is visible, but color still packs the body edge to edge and no significant irregular internal paper-white survives.
- **Mechanical black-line system**: the face and 2+2 limbs have the correct inventory and placement but use smooth constant-width curves, clean Bézier paths, mechanically repeated bends, or superficial jitter without full-length meander and within-stroke pressure variation.
- **Oil-paint overcorrection**: broad wet-looking smears, gouache masses, or oil-pastel rubbing replace the original colored-pencil and childlike crayon vocabulary.
- **Straight-segment collage**: the object is assembled from broken lines, but each individual wall, rim, limb, or facial mark remains ruler-straight.
- **Surface-only wobble**: the outline wiggles, but the rim, walls, lid, base, and perspective remain mechanically clean and symmetrical.
- **Color-pass repair**: the black-only skeleton is suitably broken, but coloring reconnects gaps, regularizes curves, or replaces it with a polished outline.
- **Monster color-only link**: a generic creature keeps only the source palette and lacks a second visual identity-DNA kind from ingredient or material; a recorded motion verb cannot satisfy the static identity gate.
- **Study-board leakage**: a study-board person, object, lettering, layout, logo, or package appears in the identity, or the mixed-media-object failure board is used as a positive generation input.
- **Small-size identity loss**: the concept works at full resolution but its source-derived body, friendly black-line face, two black-line arms, two black-line legs, two visual-DNA kinds, or ground anchor fails at 120–140 px.
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
2. Did the user explicitly choose 写实卡通 or 风味小怪兽?
3. Which source silhouette/details or flavor-DNA features identify the result in that mode?
4. Does `source-faithful` present three genuine identity variants, or does `flavor-monster` present one resolved identity master unless exploration was requested?
5. Is there explicit approval for the selected character or identity master?
6. If the user chose a fusion poster, did it preserve both the photographic product and the approved canonical monster while using one interaction verb?
7. Was environment preflight deferred until the user chose a runnable pet, and did it resolve before motion generation?
8. Is the mode-appropriate motion set present, readable, and consistently anchored: twelve v2 states for `source-faithful` or 6–10 phased v3 behaviors for `flavor-monster`?
9. Is there explicit approval for the motion preview?
10. Are runtime strips transparent and structurally valid?
11. Did both the builder and validator succeed?
12. Does the imported runner remain usable without blocking normal desktop input?

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
