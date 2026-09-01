# Mixed-Media HEYTEA-Inspired Style Guide

Read this reference for desktop-pet candidate generation. Also read it for poster work when the requested direction is crayon, collage, pencil, or mixed media.

This guide describes a visual study of user-supplied references. It captures transferable drawing grammar, not official brand assets. Never reproduce source logos, complete campaign copy, packaging labels, or the drinking-head mark unless the user supplied them, has the right to use them, and explicitly asks for them.

## Core visual system

The reference language is not a uniform cartoon outline or a fully packed crayon drawing. It is a loose collage assembled from four unequal layers:

1. thin black or muted-green pen lines establish structure;
2. heterogeneous dry media—light colored-pencil scumbling, childlike wax-crayon loops or blocks, and occasional dry pastel—supply most color;
3. pale wash or translucent blocks indicate liquid, clear plastic, light, or atmosphere;
4. occasional photographic ingredient fragments create a deliberate real-versus-drawn collision.

Do not force every layer into every image. Two or three layers are enough, but the result must retain visible material contrast.

## Line grammar

- Mix thin-to-medium pen with strategically heavier marker passages. For `flavor-monster`, the body and source-derived protrusions require one semantically complete heavy black structural stroke system, while the face and 2+2 limbs remain thinner. At any cross-section the boundary reads as one mark, never a parallel band, braid, rope, or outline-of-an-outline. Every important stroke must change pressure or thickness within itself; a complete boundary is not permission for constant-width monoline.
- Every structural stroke must visibly wander along its full length. Cup walls, rims, bases, arms, legs, and facial dashes should use short flat spots, shallow dents, drifting curvature, pressure jumps, imperfect corners, dry breaks, overshoots, or mismatched joins. For a flavor-monster boundary, allow only one or two short local retraces and keep continuous parallel travel below roughly ten percent of the complete path. Breaking ruler-straight lines into fragments, bending a smooth Bézier path, or adding surface jitter to a clean vector skeleton does not create the target hand feel.
- Allow open joins, overshooting terminals, and color that misses the outline by a few pixels.
- Keep secondary marks sparse. One loose curl, broken arc, crooked underline, or short motion dash is more faithful than dense decoration.
- Make the geometry itself structurally naive: unequal wall slopes, tilted rims, off-center openings, shifted lids, inconsistent perspective, and crooked bases. A clean template with surface wobble is not enough.

The target is an observed hand making decisions in real time. Smooth Bézier curves, mechanically rounded corners, sticker borders, identical line weight, whole-loop mechanical doubling, braided or rope-like tracks, repeated beaded stamps, and clean vector paths with a wobble filter fail this style.

## Color and material grammar

- Begin with the photographed subject's one to three identifying colors.
- Favor food-native, low-to-medium-saturation hues: tea green, yellow-green, cream, pale yellow, fruit red, and restrained brown.
- Assign media by material region instead of applying one texture to the whole character. `source-faithful` may keep loose colored pencil, wax crayon, graphite, or occasional pale wash according to source material. `flavor-monster` uses dry wax crayon as the dominant color tool.
- For `flavor-monster`, wax crayon uses a small number of broad blunt side-of-crayon sweeps with matte granular deposits, broken pressure, ragged ends, and visible paper tooth. Follow the approved material layer map: establish a continuous primary matrix, embed inclusions or deposits within it, keep surface layers spatially distinct, and overlap broad dry-wax passes to create intermediate hues and depth. Paper-white breathing space is optional and must not sever the mapped hierarchy. Slight misses or crossings at the black boundary are allowed when the boundary remains readable.
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

- `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png`: public, repo-created positive style anchor for HEYTEA-like cuteness and handmade looseness. It is not an anatomy or outline template: never copy its body topology, protrusion placement, facial-mark type/count/layout, limb attachment points, lengths, proportions, resting pose, feature coordinates, or outline treatment into a new identity.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_single_pass_rough_line_v1.png`: primary anatomy-free `flavor-monster` black-line board, assembled only from non-lettering HEYTEA source cutouts. Its isolated heavy contour curves and lighter arm/leg curves control one-pass path construction, pressure jumps, blunt terminals, crooked travel, dry breaks, bad joins, and restrained local retracing. It supplies no silhouette, face, limb skeleton, object, text, or character anatomy.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_crayon_layer_v1.png`: color-stage-only board for broad blunt dry wax-crayon, paper tooth, and optional breathing space. It supplies no color-zone structure or required gap count. Do not pass it to flavor-monster black-line-master generation, and do not copy its line fragments.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_dry_media_wavy_line_v4.png`: primary line-and-color reference for continuously meandering strokes, light colored-pencil scumbling, childlike wax-crayon loops, chunky crayon marks, and paper tooth.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_smudged_paint_structure_v3.png`: secondary reference for fading edges, paper intrusion, crooked rims, unequal walls, and shifted lids; do not let its broad smears dominate the whole character.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_figure_actions_v2.png`: faceless action figures, primitive props, gesture economy, and object-to-figure scale.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_thin_stroke_anatomy_v2.png`: thin black/green line weight, awkward glyph structure, open joins, overshoots, retracing, and dry breaks.
- `private-assets/reference-cutouts/desktop-pet-style/contact_sheet_mixed_media_objects_v2.png`: analysis-only example of an over-hatched failure. Never pass it as a positive identity-generation reference.

For `flavor-monster` black-line generation, pass the uploaded photo, public pink-green example, and the single-pass rough-line board with a separate declared role for each. Construct the face from the approved written face brief only. After the line master passes, use only the locked master, crayon-layer board, and dry-media board for color. Exclude the lettering-derived thin-stroke board from flavor-monster identity generation, use the figure-action board only during motion generation, use the smudged-paint board only for focused material repair, and keep the mixed-media-object failure board outside every positive input. No reference board may supply silhouette, face, limb skeleton, object, text, layout, logo, packaging, or anatomical coordinates.

For `source-faithful`, continue choosing the same positive controls according to the photographed object's construction needs. When these study boards ship with the open-source Skill, identify them as non-official reference assets and keep them outside the CC BY grant for original examples.

When a generated identity still has a clean cartoon framework, borrow line anatomy—not figure identity—from primary poster-mode `figures/full-poses/*` and `lettering/strokes/*` cutouts. `flavor-monster` always uses a black-line master followed by a line-locked crayon pass. Poster assets control segment construction, blunt ends, line-weight jumps, and bad joins; they must not introduce workers, lettering, props, or logos into the pet.

## Desktop-pet translation

For every `source-faithful` three-candidate board and every `flavor-monster` single identity master:

- use mode-specific hesitant pen; for `flavor-monster`, enclose the body and source-derived protrusions with a heavy irregular black boundary and keep the face plus 2+2 limbs thinner but pressure-varying;
- preserve mode-specific material layering; for `flavor-monster`, use broad blunt dry wax-crayon to preserve the primary matrix, embedded inclusions or deposits, surface layers, overlaps, optional breathing space, and selected missed edges rather than transparent wash, peer color blocks, or one equal-density texture;
- use a warm-white review background with enough separation to inspect edge quality.

For `source-faithful`:

- preserve the source silhouette, major internal divisions, identifying colors, and must-preserve object details;
- vary face placement, limb proportions, structural crookedness, and temperament only;
- reject animal costumes, monster substitution, or loss of object recognition.

For `flavor-monster`, obtain all identity decisions from `desktop-pet-character-modes.md`. This guide controls only their visual execution: heavy irregular boundary, thinner line features, broad blunt dry wax-crayon, paper tooth, optional breathing space, and the assigned reference-board stages.

For animation frames, preserve the same stroke logic even when poses change. Runtime interpolation may move or squash the complete drawing, but it must not replace hand-drawn silhouette-changing key poses.

## Rejection checklist

Reject and regenerate when any of these dominate:

- smooth, equal-width, sticker-like, whole-loop mechanically doubled, braided, rope-like, outlined-band, or repeated-stamp black outline;
- smooth vector geometry or sticker border;
- airbrushed gradient, glossy 3D volume, or plastic shading;
- transparent marker, watercolor, pastel or oil-pastel smear, smooth digital fill, or dense uniform crayon covering every region with the same mark;
- paper tooth or digital speckle presented as "white space" while color still fills the body edge to edge;
- smooth constant-width face or limb curves, including clean Bézier paths with only superficial jitter;
- more than one or two local retraces, or continuous parallel travel covering roughly ten percent or more of the complete flavor-monster boundary;
- oil-paint, oil-pastel, gouache, or wet-smear appearance dominating the character;
- ruler-straight segments, even when separated by deliberate gaps;
- structurally clean geometry with a superficial wobble filter;
- generic chibi face as the main source of cuteness;
- excessive props, decorations, text, logos, or campaign layout;
- photographic desktop-pet body with doodles merely pasted on top.
- `source-faithful` output that replaces the source object with a generic creature.
- `flavor-monster` body missing its heavy irregular structural boundary, or using a smooth equal-width/sticker-like boundary instead.
