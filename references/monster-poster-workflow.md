# Approved-Monster Fusion Poster Workflow

Read this reference only after a `flavor-monster` identity has received explicit user approval and the user chooses a fusion poster.

## Required inputs

Use both of these inputs and keep their roles separate:

1. The original uploaded photo is the sole source of the product. Preserve its photographic texture, silhouette, proportions, construction, liquid or food regions, translucency, condensation, highlights, and material cues. Background cleanup and subject cutout are allowed; redesigning, repainting, or cartoonizing the product is not.
2. The approved canonical monster is the sole identity source for the character. Lock its body topology and proportions, face layout, exactly two arms and two legs, attachment points, palette, dry-media treatment, flavor-DNA marks, and line character. Pose may change to support the interaction; identity may not.

Do not regenerate a new monster from the product photo during poster production. If the approved identity artifact is missing or ambiguous, stop and ask the user to provide or reconfirm it.

## Interaction concept

Choose one clear interaction verb per poster: `投`, `扶`, `抱`, `探`, `推`, `尝`, or another single primitive action the product can physically support.

- Make the product and monster visibly affect one another through contact, overlap, gaze, weight, direction, or a short action arc.
- Keep the action legible without explanatory copy.
- Use one main interaction, not a collage of unrelated gags.
- Remove background props that do not support the action, including loose straws or duplicated packaging when they compete with the subject.
- Preserve generous intentional white space and keep the product as the photographic anchor.

## Text poster

Read `style-guide.md` and `lettering-guide.md`. Build a composition designed for typography from the start:

1. Generate the poster base with the photographic product, approved monster, interaction, and reserved title zone, but no generated title glyphs.
2. Build the title construction sheet with `../scripts/build_title_reference_sheet.py` when applicable.
3. Create the title as a separate transparent layer and combine it with `../scripts/composite_title_layer.py` when applicable.

The title should follow the requested crooked handmade hierarchy and the source composition's planned negative space. It must not cover defining product structure, the monster's face, its 2+2 limb inventory, or the contact point of the interaction.

## No-text poster

Forbid all words, letters, numbers, captions, labels, pseudo-glyphs, signatures, and watermarks. Do not reserve an empty title box. Let the product scale, monster pose, contact point, and one interaction verb complete the story.

## Two-version rule

When the user requests both versions, design two independent compositions. Change the product placement, monster staging, balance of white space, or interaction framing so each version is resolved for its own narrative. Do not create one shared base and merely toggle the title layer.

## Review gate

Reject or revise when any of these occur:

- the photographed product's structure, material, or proportions drift;
- the product becomes illustrated, repainted, or replaced by a generated lookalike;
- the monster's body, face, limb count, attachment points, colors, material, or flavor marks drift from the approved canonical identity;
- pose adaptation silently becomes identity redesign;
- more than one interaction competes for attention, or no physical relationship is readable;
- the text version relies on image-model typography instead of the separate title workflow;
- the no-text version contains any text-like marks;
- the two versions reuse the same composition with text switched on or off;
- runner availability or installation status blocks this static poster branch.

Use `evaluation.md` for the final combined poster review.
