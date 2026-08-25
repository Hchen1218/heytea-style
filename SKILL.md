---
name: heytea-doodle-poster
description: >-
  Turn an uploaded photo into either a HEYTEA-inspired object-and-doodle poster
  or a personalized hand-drawn desktop pet with approved character concepts,
  twelve required animation states, optional fall/touch interactions, and an importable schema-v2 pet pack. Use for 喜茶简笔画海报,
  歪扭儿童字, 实物加小人涂鸦, 桌宠, 照片变桌面宠物, 食物桌宠, or 饮料桌宠.
---

# Heytea Doodle Poster and Desktop Pet

Create unofficial visual work inspired by the playful HEYTEA poster language: rough black marks, awkward handmade shapes, generous white space, and restrained object-led storytelling.

Do not add official HEYTEA logos, mascots, packaging marks, or claims of affiliation unless the user supplies authorized assets and explicitly requests their use.

## Route the request

Choose one mode before generating:

- **Poster mode**: the user wants a poster, social image, crooked Chinese title, or real-object-with-doodles composition. Read `references/style-guide.md`; for `带字版`, also read `references/lettering-guide.md`.
- **Desktop-pet mode**: the user wants a 桌宠, desktop companion, animated pet, spritesheet, or importable character pack. Read `references/desktop-pet-environment.md`, `references/desktop-pet-workflow.md`, `references/mixed-media-style-guide.md`, and `references/desktop-pet-pack.md`.
- If the request genuinely asks for both, complete the two modes independently. Do not turn a poster crop into a pet asset or reuse a pet candidate as the poster without adapting its composition.

## Shared input boundary

1. Require an uploaded image before visual generation.
2. Inspect the image before proposing output.
3. If no usable subject is visible, stop and ask for a clearer photo. Give concrete capture advice: one subject, adequate light, sharp focus, and an unobstructed outline.
4. If several independent subjects are visible, identify them with short numbered descriptions and ask the user to choose. Do not silently select one.
5. For a drink in a cup, food in a bowl, or water in a vessel, treat the container and contents as one subject unless the user asks otherwise.

## Poster mode

Keep one photographed object recognizable and photographic. Do not cartoonize the full image.

Before generating:

1. Inspect `private-assets/reference-cutouts/asset-index.json` when it exists.
2. Choose `带字版`, `无字版`, or `两套都出（推荐）`; default to two genuinely different concepts when the user wants immediate output and has not chosen.
3. For `带字版`, use the poster-base, title-construction-sheet, and title-layer workflow. Use `scripts/build_title_reference_sheet.py` and `scripts/composite_title_layer.py` when applicable.
4. For `无字版`, forbid all text and let one primitive micro-worker action tell the story.

Use `references/evaluation.md` for final review.

## Desktop-pet mode

The photographed subject becomes the character body. Do not preserve photographic texture as the poster mode does.

Follow the approval gates exactly:

1. Run `scripts/check_desktop_pet_environment.py --json` before inspecting or generating the photo. If the runner or required toolchain is missing, explain the exact repair plan and ask whether to install it. Run `scripts/install_desktop_pet_runtime.py` only after explicit approval, then rerun preflight. Do not silently install software, bypass operating-system warnings, or enable launch-at-login.
2. Resolve the subject using the shared input boundary.
3. Inspect the five desktop-pet boards listed in `references/mixed-media-style-guide.md`: use the dry-media, action, and stroke boards as primary controls; use the smudged-paint board only for crooked structure; treat the mixed-media-object board as an `avoid-default` failure example. Then extract the subject's silhouette, one to three identifying colors, and the features that must stay recognizable.
4. Generate one white or warm-white candidate board containing three genuine identity variants in the same neutral front-facing stance and at the same ground anchor. Keep source identity and palette stable; vary only face system, limb proportions, structural crookedness, and stable temperament—not action or pose. For mixed-media drinks and soft foods, use the two-pass candidate construction in `references/desktop-pet-workflow.md`: first approve a skeleton in which every stroke visibly meanders, then lock every line while assigning different dry media—colored pencil, childlike wax crayon, or sparse pale wash—to different material regions. Do not substitute ruler-straight segments, one uniform fill texture, oil-paint smears, a clean template with surface wobble, or a smooth digital gradient.
5. Ask the user to select or revise a candidate. If the three images differ only by pose, treat that as a failed candidate board: consolidate their shared identity into one neutral canonical master and reuse the discarded poses only as motion ideas. Do not generate motion assets before the user explicitly approves the identity or consolidation.
6. Generate the twelve required actions described in `references/desktop-pet-workflow.md`, plus `fall` and `touch` when the requested runner includes high-drop or cursor-touch behavior. Use the canonical master as the sole identity reference and apply the small-size stability gate before presenting the dynamic review sheet.
7. Ask the user to approve motion. Do not package unapproved motion assets.
8. After approval, export transparent animation strips, build the pack and platform delivery folder with `scripts/build_desktop_pet_pack.py --delivery-dir ...`, and validate the ZIP with `scripts/validate_desktop_pet_pack.py`.
9. Return the review artifacts, validated ZIP, manifest summary, and delivery folder. The shared Electron runner is installed once; each pet folder contains only its pack, preview, start/quit entrypoints, and short usage note.

For a schema-v1 pack, preserve the original pack, copy its eight actions into a new v2 draft, stabilize them, generate `curious`, `stretch`, `tiptoe`, and `play` from the canonical identity, and require a fresh motion approval. Never overwrite or silently activate the v1 pack.

White backgrounds are for candidate and motion review only. Runtime animation files must have real alpha transparency.

## Output boundary

- Never describe exploratory image-model output as a finished pet pack.
- Do not fabricate file paths, validation results, or runnable installers.
- If visual generation is unavailable, return the staged prompt packet and pack specification, and state which artifacts still need to be generated.
- Treat official-looking marks, private-study-only cutouts, and `quality: avoid-default` records as analysis-only.
- Preserve user files and unrelated working-tree changes when running scripts or packaging output.

## Evaluation

Use `references/evaluation.md` for poster and desktop-pet acceptance checks. Human visual approval is mandatory at both desktop-pet gates; automated validation cannot replace it.
