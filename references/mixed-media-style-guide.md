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
- For a `source-faithful` desktop pet, the photographed object remains the body. For a `flavor-monster` desktop pet, the approved creature remains the body; the photo supplies color, ingredient, material, and body topology as static visual identity DNA, while its motion verb is reserved for later behavior design. Every flavor-monster face mark and all four limbs use sparse black doodle lines.
- Keep the two arms and two legs short, open, black, and slightly clumsy. Let pose, tilt, squash, crumbs, bubbles, steam, or wobble carry emotion.

## Model-facing reference boards

Inspect these boards before writing an identity or action prompt:

- `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png`: public, repo-created positive style anchor for HEYTEA-like cuteness, handmade awkwardness, and the relationship between a mostly unoutlined color body and sparse black doodle face/limbs. Never copy its body topology, protrusion placement, face layout, or proportions into a new identity.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_dry_media_wavy_line_v4.png`: primary line-and-color reference for continuously meandering strokes, light colored-pencil scumbling, childlike wax-crayon loops, chunky crayon marks, and paper tooth.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_smudged_paint_structure_v3.png`: secondary reference for fading edges, paper intrusion, crooked rims, unequal walls, and shifted lids; do not let its broad smears dominate the whole character.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_figure_actions_v2.png`: faceless action figures, primitive props, gesture economy, and object-to-figure scale.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_thin_stroke_anatomy_v2.png`: thin black/green line weight, awkward glyph structure, open joins, overshoots, retracing, and dry breaks.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_mixed_media_objects_v2.png`: analysis-only example of an over-hatched failure. Never pass it as a positive identity-generation reference.

For `flavor-monster` identity generation, pass the uploaded photo, the public pink-green example, the dry-media/wavy-line board, and the thin-stroke board, with a separate declared role for each. The photo supplies color, ingredient, material, and body-topology DNA while its motion verb is reserved for later behavior design; the public example controls only cuteness, handmade awkwardness, and the relationship between an unoutlined color body and black doodle face/limbs; the dry-media board controls crayon and paper texture; and the stroke board controls the black line quality of exactly two arms, two legs, and every facial mark. State explicitly that the public example must not supply silhouette, protrusion placement, face layout, or proportions. Use the figure-action board only during motion generation after identity approval. Use the smudged-paint board only for focused repair of a failed body axis. Do not copy any depicted object, person, lettering, layout, logo, or packaging. Keep the mixed-media-object board outside every positive generation input and consult it only when diagnosing over-hatched output.

For `source-faithful`, continue choosing the same positive controls according to the photographed object's construction needs. When these study boards ship with the open-source Skill, identify them as non-official reference assets and keep them outside the CC BY grant for original examples.

When a generated identity still has a clean cartoon framework, borrow line anatomy—not figure identity—from primary poster-mode `figures/full-poses/*` and `lettering/strokes/*` cutouts. Use a black-only skeleton and locked-color repair only then for `flavor-monster`; its default identity pass is complete color with regional media already assigned. Poster assets control segment construction, blunt ends, line-weight jumps, and bad joins; they must not introduce workers, lettering, props, or logos into the pet.

## Desktop-pet translation

For every `source-faithful` three-candidate board and every `flavor-monster` single identity master:

- use thin-to-medium hesitant pen only where the selected mode calls for line structure; for `flavor-monster`, concentrate black linework in the face, two arms, two legs, and sparse partial marks rather than enclosing the body;
- zone drinks and soft foods across light colored pencil, broad childlike wax crayon, paper-white clear areas, and only occasional pale smear; never give the full body one uniform texture;
- use a warm-white review background with enough separation to inspect edge quality.

For `source-faithful`:

- preserve the source silhouette, major internal divisions, identifying colors, and must-preserve object details;
- vary face placement, limb proportions, structural crookedness, and temperament only;
- reject animal costumes, monster substitution, or loss of object recognition.

For `flavor-monster`:

- preserve at least two kinds of visual identity DNA chosen from color, ingredient, and material instead of the photographed container silhouette, and record motion DNA separately for later behavior design;
- derive a soft, compact, friendly, animatable body topology and center of gravity from the source DNA without preserving a literal source-object silhouette;
- keep the body a dry-media color mass without a complete black enclosing outline;
- draw exactly two arms and two legs as separate, open, crooked black doodle strokes; never use colored or volumetric limbs, paws, toes, realistic joints, tendrils, trailing flesh, or another limb inventory;
- draw every facial mark as a sparse, friendly black doodle line; allow one or two eyes, offset layouts, or no conventional mouth, but reject colored features, realistic or shaded eyes, large chibi eyes, and complex facial anatomy;
- translate ingredients into abstract blocks, spots, paper gaps, local media changes, or restrained irregularities rather than a mushroom ear, fruit horn, topping hat, or other realistic organ;
- default to one best complete-color concept with a source-driven body, black-line face, fixed 2+2 black-line limbs, stable temperament, quiet resting pose, scale, and ground anchor;
- require a cuteness pass: reject fleshy collapse, exposed or realistic tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, or any disturbing organic reading;
- generate multiple identity directions only when the user explicitly requests exploration;
- reject complete cup, bowl, bottle, wrapper, pizza slice, mushroom, ingredient, or other literal source-object silhouettes;
- reject generic unrelated monsters whose palette could be changed without losing all connection to the source.

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
- `source-faithful` output that replaces the source object with a generic creature.
- `flavor-monster` output that is still a cup, bowl, bottle, wrapper, or food package with limbs.
- `flavor-monster` identity output that copies source colors but omits both ingredient and material DNA, or later behavior output that ignores the separately recorded motion DNA.
- `flavor-monster` body with a complete enclosing black outline instead of an unoutlined dry-media color mass.
- colored, volumetric, missing, merged, or tendril-replaced limbs instead of exactly two open black-line arms and two open black-line legs.
- colored facial blobs, realistic or shaded eyes, large chibi eyes, complex facial anatomy, or facial marks that are not sparse black doodle lines.
- literal ingredient anatomy or a complete pizza slice, mushroom, cup, or other source-object silhouette.
- fleshy collapse, exposed tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, or another disturbing organic reading.
- correct crayon or pencil medium applied without the public example's cuteness and black-line face/limb relationship, or with its silhouette and face layout copied as a template.
