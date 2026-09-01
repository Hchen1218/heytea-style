# Desktop-Pet Character Modes

Read this reference for every desktop-pet request after resolving the photo subject and before extracting identity or generating candidates.

## Mandatory mode choice

Desktop-pet mode has two parallel character modes. Neither is a fallback for the other. They share the runtime, approval gates, and delivery format, but deliberately use different public pack protocols.

If the user has not already selected a mode, stop before visual generation and ask:

1. **写实卡通桌宠**：保留照片主体的原始轮廓与关键结构，把主体本身手绘角色化。
2. **风味小怪兽桌宠**：提取照片的颜色、材质、配料和特征动作，重新设计成独立的小怪兽，不保留容器轮廓。

Do not choose a default, infer the mode from whether the subject is food or drink, or generate both unless the user explicitly asks for both. If the user names one mode in the request, proceed without asking again.

Record the chosen value as `source-faithful` or `flavor-monster` and keep it fixed through character approval, motion approval, and packaging. Changing mode requires a fresh character approval; it does not require a different runner.

## Mode A: 写实卡通桌宠 (`source-faithful`)

### Character identity

- The photographed subject becomes the character body.
- Preserve its outer silhouette, orientation, major internal divisions, one to three identifying colors, and two to four must-preserve details.
- A container and its contents remain one visible unit by default.
- Simplify photographic texture into the shared hesitant-line and mixed-media grammar, but do not replace the subject with an unrelated animal, mascot, or monster body.
- Candidate differences come from face placement, limb proportions, structural crookedness, and stable temperament—not different source objects or action poses.

### Action and behavior identity

- Base `signature` and `play` on a real property of the subject: bubbles, wobble, crumbs, rolling, steam, melting, light, or another source-specific verb.
- Let rigid objects move through tilt, hinge, roll, or appendage gesture; let liquids and soft foods move through slosh, squash, ripple, bubble, or settle.
- Keep actions subordinate to source recognition. A pose must not redesign the container, label-free package, food shape, or object structure.

## Mode B: 风味小怪兽桌宠 (`flavor-monster`)

### Source DNA

The photograph supplies flavor DNA rather than a body template. Separate what the static identity must prove from what later behavior must express.

Extract visual identity DNA:

- one to three identifying colors;
- one or two ingredient/material cues, such as fruit cubes, pearls, foam, bubbles, crumbs, glaze, leaves, or transparency;
- one required non-color structural memory from ingredient, material, source shape, or processing trace that can become an abstract silhouette feature. Use at least one and normally one or two ear-like fins, horns, crests, spines, tail buds, antennae, or comparable protrusions; color, texture, spots, and internal marks alone do not satisfy this requirement.

Also record one source-specific motion verb as behavior DNA for the later action stage. It does not count toward the static identity minimum.

Before drawing, write a compact internal identity brief. Use no more than three identifying visual source signals, but do not treat them as peers. First build a `source relation map`:

`source signal → source role → relation → creature role → abstraction method → body attachment or material layer`

Assign each signal exactly one source role: `primary-matrix`, `embedded-inclusion`, `surface-layer`, `deposit`, or `accent`. Record position and containment separately with `embedded-in`, `sits-on-top-of`, `accumulates-at`, and `overlaps-with`. Preserve hierarchy, containment, and position before abstraction. A color does not become an independent monster zone merely because it is visually distinct. For example, a pink drink with yellow fruit pieces settled inside it and a green topping above it maps to one pink `primary-matrix`, yellow `embedded-inclusion` signals that `accumulates-at` the bottom, and one green `surface-layer` that `sits-on-top-of` the matrix; it does not map to three peer color blocks.

Use at least two kinds of visual identity DNA chosen from color, ingredient, and material. A generic monster whose only connection to the photo is a replaceable palette fails even when a motion verb has been recorded. Extend the brief with:

- a source-derived body silhouette and center of gravity that do not copy the public example or retain the literal source object;
- a `DNA → monster structure` map that names at least one non-color source signal, its abstract silhouette feature, how it avoids literal ingredient anatomy, and where it joins the body. The feature must alter the outer contour and remain legible at 120–140 px; a generic disk, dome, or blob with only recoloring or internal decoration fails;
- an `example difference lock` that names the public example's facial-mark system and limb skeleton as discard-only anatomy, then declares a different facial-mark type/count/layout and different arm/leg attachment points, lengths, proportions, and resting geometry for the new identity. The example may guide line quality and cuteness, never anatomical coordinates or skeleton;
- an `outline construction brief` that declares the source-derived body boundary and protrusions, line-weight hierarchy, and specific locations for short flat spots, shallow dents, blunt corners, hesitant bends, pressure jumps, dry breaks, overshoots, or slightly mismatched joins. Treat the boundary as one stroke system at every cross-section; allow only one or two short local retraces and keep continuous parallel travel below roughly ten percent of the complete path. The body boundary is the heaviest system; face and limbs remain thinner but visibly handmade;
- a `face construction brief` that defaults to two unmistakable eyes on a readable eye level and one unmistakable friendly mouth below them. Apply `readability > friendliness > identity distinctiveness > handmade irregularity`. A viewer who has not read the brief must identify both eyes and the mouth at 120–140 px. Use only mild handmade differences in size, tilt, line weight, pressure, or terminals; do not require every face mark to bend, break, or jump pressure. Clear bean eyes, dot eyes, simple smiles, near-centered spacing, and U-like mouths are allowed when they remain hand-drawn rather than copied stock emoji. Single-eyed, mouthless, broken-hook, or otherwise experimental systems require an explicit user request. Reject realistic or shaded eyes, highlights, large chibi eyes, complex facial anatomy, and direct copies of existing emoji or the public example's face;
- a `material layer map` that establishes a continuous primary matrix before assigning embedded inclusions, deposits, surface layers, accents, broad blunt dry wax-crayon travel, optional paper-white breathing space, and selected missed or faded edges. Preserve the `source relation map`: inclusions stay embedded, deposits keep their concentration or position, and surface layers stay spatially distinct while broad dry-wax overlap may create intermediate hues and depth. Paper-white has no minimum count and must not divide related layers into peer blocks. No layer may collapse into transparent marker, dense micro-patterns, smooth digital gradient, or one equal-density fill;
- exactly two arms and two legs, including their black-line attachment points, lengths, proportions, and quiet resting pose. Source-derived ears, fins, horns, crests, spines, tail buds, antennae, or comparable silhouette features remain colored body topology and never count as, replace, or imitate one of the four limbs;
- a cuteness check: the body must read as soft, compact, friendly, and animatable before it reads as strange;
- hard exclusions for fleshy collapse, exposed or realistic tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, and other disturbing organic readings;
- a stable floor anchor and source-specific motion verbs reserved for later behavior design;
- a discard list for the complete cup, bottle, bowl, wrapper, rim, lid, straw, container wall, layered-liquid cross-section, pizza slice, mushroom, or other literal source-object silhouette whenever present.

The brief guides generation; do not save the full generation prompt as a project document unless the user explicitly requests it.

### Character identity

- The first impression must be a cute, friendly, independent doodle creature; source recognition comes second through flavor DNA. A visually unpleasant or uncanny body fails even when its source mapping is accurate.
- Use `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png` only as the positive style anchor for HEYTEA-like cuteness and handmade looseness. Use `contact_sheet_single_pass_rough_line_v1.png`, assembled only from non-lettering HEYTEA source cutouts, for heavy boundary curves and lighter arm/leg curves; it supplies no object, face, text, or anatomy. Construct facial marks from the written face construction brief without any face-mark image board. Reserve `contact_sheet_crayon_layer_v1.png` for broad dry wax-crayon, paper tooth, and optional breathing space during the color stage; it supplies no color-zone structure or required gap count. Do not copy the public example's body topology, protrusion placement, facial-mark type/count/layout, limb attachment points, limb lengths or proportions, resting pose, or anatomical coordinates. A new silhouette with the same face-and-limb skeleton is still a copy and fails.
- Derive the body's soft, compact silhouette and center of gravity from the source brief. Do not preserve a literal pizza slice, cup, mushroom, ingredient, container, or photographed food silhouette, and do not turn irregularity into flesh, slime, horror anatomy, or corpse-like collapse.
- Draw exactly two arms and two legs as separate, open, crooked black doodle strokes. Each stroke must wander or bend along its full length and change pressure or thickness within the same mark, with restrained dry breaks, retracing, overshoots, or open joins. Keep them visibly black, light-to-thin, dry, slightly clumsy, and readable; reject smooth Bézier curves, constant-width monoline, superficial jitter on a clean vector path, colored strokes, tendrils, trailing body material, volumetric paws, mittens, feet, toes, or realistic joints.
- Render the face exactly from the `face construction brief`; do not derive its anatomy from an image board or the public example.
- Convert source colors, ingredients, and materials into crude flat marks, paper gaps, local crayon changes, and at least one contour-changing abstract monster feature. Acceptable roles include an ear-like fin, horn, crest, spine, tail bud, antenna, or another compact protrusion derived from the source; do not turn a mushroom, fruit, pearl, leaf, or topping into a recognizable realistic organ. Reject decorative ears or tails with no traceable source mapping.
- Enclose the source-derived body and its monster protrusions with one semantically complete black structural stroke system. At every cross-section it reads as one mark rather than a parallel band, braid, rope, or outlined strip. It must be heavier than the face and limbs and change the underlying path through flat spots, shallow dents, blunt corners, hesitant bends, pressure jumps, dry breaks, overshoots, or slightly mismatched joins. Allow one or two short local retraces only; continuous parallel travel must stay below roughly ten percent of the complete boundary. Reject smooth equal-width contours, polished sticker borders, whole-loop mechanical doubling, repeated beaded stamps, and a clean vector skeleton with surface jitter.
- Build color from the `material layer map`: lay down a coherent primary matrix, embed inclusions or deposits within it, keep surface layers spatially distinct, and use overlapping broad blunt matte wax-crayon passes to create intermediate hues and depth. Preserve granular drag, paper tooth, broken pressure, ragged ends, selected misses, faded ends, and slight boundary crossings. Paper-white breathing space is optional and has no minimum count; when present, it must support rather than sever the mapped relationships. Transparent marker, watercolor, pastel or oil-pastel smear, smooth digital fill or gradient, uniform noise, dense tiny strokes or loops, short hatching, or crosshatching fails.
- Default to one best identity in a quiet identity-readable resting pose rather than a three-candidate board, but construct it in two locked stages: approve the black-line master at full size, a 300% detail crop, and 120–140 px, then add color behind it without changing any black mark. If one focused repair leaves a multi-track or smooth inherited outline, discard that inherited line skeleton and rebuild a fresh black-line master from the locked topology instead of stacking another edit. Lock the source-derived body, source relation map, heavy boundary, two black-line arms, two black-line legs, black-line face system, material layer map, stable temperament, scale, and ground anchor. Generate multiple directions only when the user explicitly asks for exploration.

Write both sides of the model instruction: a positive cute flat-doodle definition and hard exclusions for container or literal food anatomy, smooth equal-width or sticker-like enclosing borders, colored or volumetric limbs, missing arms or legs, tendril substitution, realistic facial features, large chibi eyes, fleshy collapse, slime, horror anatomy, official marks, text, polished vector geometry, and glossy 3D treatment. Do not merely attach limbs to the photographed object.

### Action identity

- Use mark-led secondary motion: a crude flat mark, abstract protrusion, paper gap, or local crayon patch reacts before or after the whole body without becoming a literal organ.
- Define 6–10 complete schema-v3 behaviors around the approved graphic identity rather than filling a fixed action-name checklist.
- Include bindings for awake idle, sleep, click, pointer encounter, drag, release, and at least one ambient behavior.
- Sleep must visibly enter, persist in a loop, and wake through an exit; exploration, cursor encounter, held, and drop recovery may also use explicit phases.
- Give each behavior enough amplitude and internal progression to read as one story. Prefer fewer substantial behaviors over many tiny interchangeable gestures.
- Flavor events such as a block-mark hiccup, one bubble, color ripple, or abstract-protrusion shake should arise from an approved mark or internal feature, not a generic prop.
- Drag, fall, impact, rebound, and settle must preserve the monster's graphic identity and connect physically; the approved abstract protrusion or local mark may lag or settle, but the two black-line arms, two black-line legs, and black-line face system must remain stable.

## Shared production contract

Both character modes use:

- the same environment preflight and installed shared runner, loaded only after canonical identity approval when the user chooses runnable motion;
- the same black-skeleton then locked-color construction; `source-faithful` keeps its existing candidate use, while `flavor-monster` always approves one heavy-boundary line master before the relation-preserving material-layer pass;
- the same explicit character-approval and motion-approval gates;
- the same 120–140 px readability target, transparent runtime strips, version-aware builder and validator, and delivery folder.

The public formats remain intentionally separate: `source-faithful` uses schema v2 with twelve required actions and optional `fall` / `touch`; `flavor-monster` uses schema v3 with 6–10 reachable behaviors and explicit phases. Both compile to one internal runtime model. Do not migrate existing v2 packs or duplicate the Electron runtime.
