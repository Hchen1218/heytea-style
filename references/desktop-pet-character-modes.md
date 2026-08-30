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
- optional structural memory that can become one crude flat mark, paper gap, local media shift, or abstract irregular protrusion.

Also record one source-specific motion verb as behavior DNA for the later action stage. It does not count toward the static identity minimum.

Before drawing, write a compact internal identity brief. Use no more than three identifying visual source signals and map each one to one creature role:

`source color / ingredient / material → crayon body field / crude flat mark / abstract irregular protrusion / regional medium`

Use at least two kinds of visual identity DNA chosen from color, ingredient, and material. A generic monster whose only connection to the photo is a replaceable palette fails even when a motion verb has been recorded. Extend the brief with:

- a source-derived body silhouette and center of gravity that do not copy the public example or retain the literal source object;
- a regional material plan that assigns every major body zone to long loose lightly layered colored-pencil sweeps, a small number of broad open wax-crayon arcs or separated blocks, significant irregular internal paper-white, or an occasional faded edge; light regions may be mostly paper-white with only faint marks, and no two unlike regions may be flattened into one equal-density texture;
- exactly two arms and two legs, including their black-line attachment points, lengths, proportions, and quiet resting pose;
- facial-mark count, placement, line shape, and friendly emotion; the face may be single-eyed, mouthless, offset, or otherwise structurally variable. For the face and every limb, declare where the stroke meanders or bends and which within-stroke pressure change, thickness jump, dry break, retracing, overshoot, or open join keeps it visibly handmade;
- a cuteness check: the body must read as soft, compact, friendly, and animatable before it reads as strange;
- hard exclusions for fleshy collapse, exposed or realistic tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, and other disturbing organic readings;
- a stable floor anchor and source-specific motion verbs reserved for later behavior design;
- a discard list for the complete cup, bottle, bowl, wrapper, rim, lid, straw, container wall, layered-liquid cross-section, pizza slice, mushroom, or other literal source-object silhouette whenever present.

The brief guides generation; do not save the full generation prompt as a project document unless the user explicitly requests it.

### Character identity

- The first impression must be a cute, friendly, independent doodle creature; source recognition comes second through flavor DNA. A visually unpleasant or uncanny body fails even when its source mapping is accurate.
- Use `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png` only as the positive style anchor for HEYTEA-like cuteness, handmade awkwardness, and the relationship between a mostly unoutlined dry-media color body and sparse black doodle face/limbs. Do not copy its body topology, protrusion placement, face layout, or proportions.
- Derive the body's soft, compact silhouette and center of gravity from the source brief. Do not preserve a literal pizza slice, cup, mushroom, ingredient, container, or photographed food silhouette, and do not turn irregularity into flesh, slime, horror anatomy, or corpse-like collapse.
- Draw exactly two arms and two legs as separate, open, crooked black doodle strokes. Each stroke must wander or bend along its full length and change pressure or thickness within the same mark, with restrained dry breaks, retracing, overshoots, or open joins. Keep them visibly black, light-to-thin, dry, slightly clumsy, and readable; reject smooth Bézier curves, constant-width monoline, superficial jitter on a clean vector path, colored strokes, tendrils, trailing body material, volumetric paws, mittens, feet, toes, or realistic joints.
- Draw every facial mark with the same sparse black doodle-line logic and within-stroke variation. The face may use one or two eyes, an offset layout, or no conventional mouth, but it must remain friendly and readable; reject colored facial blobs, realistic or shaded eyes, eye sockets, large chibi eyes, complex facial anatomy, smooth equal-width marks, and mechanically repeated curves.
- Convert source colors, ingredients, and materials into crude flat marks, paper gaps, local crayon changes, or restrained abstract irregularities. Do not turn a mushroom, fruit, pearl, leaf, or topping into a recognizable realistic organ.
- Keep significant irregular paper-white visible inside the body as an active material. Build colored zones with region-specific pencil or crayon behavior and allow selected misses, faded ends, or slight boundary crossings. Paper tooth under a fully saturated body does not count, and uniform noise, dense tiny strokes or loops, crosshatching, or one equal-density fill across every region fails.
- Keep the body free of a complete black enclosing outline. Avoid stacked mascot traits, a belly panel, blush, a conventional head/body partition, or shaded volume.
- Default to one best complete-color identity concept in a quiet identity-readable resting pose rather than a three-candidate board. Lock the source-derived body, two black-line arms, two black-line legs, black-line face system, stable temperament, scale, and ground anchor. Generate multiple directions only when the user explicitly asks for exploration.

Write both sides of the model instruction: a positive cute flat-doodle definition and hard exclusions for container or literal food anatomy, complete enclosing body outlines, colored or volumetric limbs, missing arms or legs, tendril substitution, realistic facial features, large chibi eyes, fleshy collapse, slime, horror anatomy, official marks, text, sticker borders, polished vector geometry, and glossy 3D treatment. Do not merely attach limbs to the photographed object.

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
- the same black-skeleton then locked-color repair process when mixed-media construction needs it; `source-faithful` keeps its existing candidate use, while `flavor-monster` defaults to one-pass complete-color identity generation;
- the same explicit character-approval and motion-approval gates;
- the same 120–140 px readability target, transparent runtime strips, version-aware builder and validator, and delivery folder.

The public formats remain intentionally separate: `source-faithful` uses schema v2 with twelve required actions and optional `fall` / `touch`; `flavor-monster` uses schema v3 with 6–10 reachable behaviors and explicit phases. Both compile to one internal runtime model. Do not migrate existing v2 packs or duplicate the Electron runtime.
