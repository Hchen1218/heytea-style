# Mixed-Media HEYTEA-Inspired Style Guide

Read this reference for desktop-pet candidate generation. Also read it for poster work when the requested direction is crayon, collage, pencil, or mixed media.

This guide describes a visual study of user-supplied references. It captures transferable drawing grammar, not official brand assets. Never reproduce source logos, complete campaign copy, packaging labels, or the drinking-head mark unless the user supplied them, has the right to use them, and explicitly asks for them.

## Core visual system

The reference language is not a uniform cartoon outline or a fully colored crayon drawing. It is a loose collage assembled from four unequal layers:

1. thin black or muted-green pen lines establish structure;
2. heterogeneous dry media—light colored-pencil scumbling, childlike wax-crayon loops or blocks, and occasional dry pastel—supply most color;
3. pale wash or translucent blocks indicate liquid, clear plastic, light, or atmosphere;
4. occasional photographic ingredient fragments create a deliberate real-versus-drawn collision.

Do not force every layer into every image. Two or three layers are enough, but the result must retain visible material contrast.

## Line grammar

- Mix thin-to-medium pen with a few strategically heavier marker passages. Do not use one uniform outline around everything.
- Every structural stroke must visibly wander along its full length. Cup walls, rims, bases, arms, legs, and facial dashes should use shallow waves, drifting curvature, pressure wobble, imperfect corners, dry breaks, retracing, or doubled corrections. Breaking ruler-straight lines into fragments does not create the target hand feel.
- Allow open joins, overshooting terminals, and color that misses the outline by a few pixels.
- Keep secondary marks sparse. One loose curl, broken arc, crooked underline, or short motion dash is more faithful than dense decoration.
- Make the geometry itself structurally naive: unequal wall slopes, tilted rims, off-center openings, shifted lids, inconsistent perspective, and crooked bases. A clean template with surface wobble is not enough.

The target is an observed hand making decisions in real time. Smooth Bézier curves, mechanically rounded corners, sticker borders, and identical line weight fail this style.

## Color and material grammar

- Begin with the photographed subject's one to three identifying colors.
- Favor food-native, low-to-medium-saturation hues: tea green, yellow-green, cream, pale yellow, fruit red, and restrained brown.
- Assign media by material region instead of applying one texture to the whole character. Light liquid or soft color may use loose colored-pencil scumbling; vivid topping or fruit may use broad childlike wax-crayon loops and chunky marks; clear plastic may remain paper-white with a few faint graphite traces.
- Colored-pencil marks should be long, loose, lightly layered, and visibly granular. Wax crayon should use a small number of broad wandering arcs, open loops, or separate blocks. Both leave substantial paper visible and may miss or cross boundaries.
- Broad rubbed pigment or pale wash is an occasional accent, not the dominant default. Oil-paint, oil-pastel smear, gouache mass, wet watercolor bloom, dense repeated tiny strokes, crosshatching, airbrushed gradients, soft plastic shading, glossy highlights, and uniform digital noise are forbidden.
- Black is structural rather than dominant. White or warm white remains an active material, not merely unused background.
- Photographic fragments, when used, should be small ingredient accents. Do not turn the entire desktop-pet body back into a photo.

## Composition and character grammar

- Preserve generous negative space. Review boards should feel like objects placed on paper, not a filled sticker sheet.
- Cuteness comes from awkward scale, a clear verb, and the relationship between body and prop—not from large eyes or a detailed face.
- Human figures are faceless, back-facing, or reduced to functional contours. Limbs bend simply and may be anatomically naive.
- For a desktop pet, the photographed object remains the body. Use only tiny, sparse facial marks when an action cannot otherwise be read.
- Keep appendages short and slightly clumsy. Let pose, tilt, squash, crumbs, bubbles, steam, or wobble carry emotion.

## Model-facing reference boards

Inspect these boards before writing a candidate or action prompt:

- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_dry_media_wavy_line_v4.png`: primary line-and-color reference for continuously meandering strokes, light colored-pencil scumbling, childlike wax-crayon loops, chunky crayon marks, and paper tooth.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_smudged_paint_structure_v3.png`: secondary reference for fading edges, paper intrusion, crooked rims, unequal walls, and shifted lids; do not let its broad smears dominate the whole character.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_figure_actions_v2.png`: faceless action figures, primitive props, gesture economy, and object-to-figure scale.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_thin_stroke_anatomy_v2.png`: thin black/green line weight, awkward glyph structure, open joins, overshoots, retracing, and dry breaks.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_mixed_media_objects_v2.png`: analysis-only example of an over-hatched failure. Do not use it as the default color-material reference.

Use the primary dry-media/wavy-line board together with the action and stroke boards, not as content to copy. The dry-media board controls continuous line motion and material zoning, the action board controls anatomy, and the stroke board controls joins and pressure. Use the smudged-paint board only as secondary structural support. When these study boards ship with the open-source Skill, identify them as non-official reference assets and keep them outside the CC BY grant for original examples.

When a generated object still has a clean cartoon framework, borrow line anatomy—not figure identity—from primary poster-mode `figures/full-poses/*` and `lettering/strokes/*` cutouts. Generate a black-only skeleton before applying color. Poster assets control segment construction, blunt ends, line-weight jumps, and bad joins; they must not introduce workers, lettering, props, or logos into the pet.

## Desktop-pet translation

For the three-candidate board:

- preserve the source silhouette, major internal divisions, and identifying colors;
- draw structural edges with thin-to-medium hesitant pen, not one smooth heavy contour;
- zone drinks and soft foods across light colored pencil, broad childlike wax crayon, paper-white clear areas, and only occasional pale smear; never give the full body one uniform texture;
- vary face placement, limb proportions, and temperament only;
- use a warm-white review background with enough separation to inspect edge quality.

For animation frames, preserve the same stroke logic even when poses change. Runtime interpolation may move or squash the complete drawing, but it must not replace hand-drawn silhouette-changing key poses.

## Rejection checklist

Reject and regenerate when any of these dominate:

- uniform thick black outline;
- smooth vector geometry or sticker border;
- airbrushed gradient, glossy 3D volume, or plastic shading;
- dense uniform crayon or pencil fill covering every region with the same mark;
- oil-paint, oil-pastel, gouache, or wet-smear appearance dominating the character;
- ruler-straight segments, even when separated by deliberate gaps;
- structurally clean geometry with a superficial wobble filter;
- generic chibi face as the main source of cuteness;
- excessive props, decorations, text, logos, or campaign layout;
- photographic desktop-pet body with doodles merely pasted on top.
