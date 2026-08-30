---
name: heytea-doodle-poster
description: >-
  Turn an uploaded photo into a HEYTEA-inspired text or no-text object-and-doodle
  poster, a static flavor monster, a poster pairing the unchanged photographed
  product with an approved monster, or an approved runnable desktop pet. Use for
  喜茶简笔画海报, 歪扭儿童字, 实物加小人涂鸦, 风味小怪兽, 小怪兽融合海报,
  桌宠, 照片变桌面宠物, 食物桌宠, or 饮料桌宠.
---

# Heytea Doodle Poster, Flavor Monster, and Desktop Pet

Create unofficial visual work inspired by the playful HEYTEA poster language: rough black marks, awkward handmade shapes, generous white space, and restrained object-led storytelling.

Do not add official HEYTEA logos, mascots, packaging marks, or claims of affiliation unless the user supplies authorized assets and explicitly requests their use.

## Photo entry and routing

Require and inspect an uploaded image before visual generation. Resolve the subject first:

- If no usable subject is visible, stop and ask for one sharp, well-lit, unobstructed subject.
- If several independent subjects are visible, give short numbered descriptions and ask which one to use. Do not silently choose.
- Treat a container and its contents as one subject unless the user asks otherwise.

When the user uploads a usable photo without saying what to make, offer exactly these three choices and do not generate or run environment checks yet:

1. 生成带字版海报
2. 生成不带字海报
3. 生成一张风味小怪兽

If the user already asked for a text poster, no-text poster, flavor monster, or both poster versions, enter that workflow directly without repeating the chooser. “两套都出” remains supported but is not a fourth default choice. An explicit 写实卡通桌宠 or `source-faithful` request remains supported but is not shown in the default three choices.

## Ordinary poster

Read `references/style-guide.md`; for `带字版`, also read `references/lettering-guide.md`.

- Keep the photographed object recognizable and photographic. Do not cartoonize the full image.
- Inspect `private-assets/reference-cutouts/asset-index.json` when it exists.
- A text poster uses separate poster-base, title-construction-sheet, and title-layer steps. Use `scripts/build_title_reference_sheet.py` and `scripts/composite_title_layer.py` when applicable.
- A no-text poster forbids all text and lets one primitive micro-worker action tell the story.
- When making both versions, create two genuinely different concepts and compositions rather than toggling a title on one base image.

Use `references/evaluation.md` for final review.

## Static flavor-monster identity

Read `references/desktop-pet-character-modes.md`, the identity stages of `references/desktop-pet-workflow.md`, and `references/mixed-media-style-guide.md`. Do not read or run the environment workflow yet.

Generate one best complete-color `flavor-monster` identity on white or warm white. The photo controls flavor DNA and body topology; `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png` controls only HEYTEA-like cuteness and the relationship between an unoutlined color body and sparse black doodle features. Use the dry-media board for body material and the thin-stroke board for the face and exactly two arms plus two legs. Do not copy the example's silhouette, protrusions, face layout, or proportions.

Inspect the identity at full size and 120–140 px, then ask the user to approve it or request a focused revision. Do not generate a poster, motion, runtime assets, or package before explicit identity approval. Approval establishes the canonical identity shared by later fusion-poster and desktop-pet branches.

After approval, ask whether to:

1. 制作融合海报；
2. 继续制作可运行桌宠；
3. 两者都做。

## Approved-monster fusion poster

Read `references/monster-poster-workflow.md` plus the ordinary poster references needed for the requested variant. Ask whether the user wants 带字版、无字版或两套都做 unless already stated.

Use the original uploaded photo and the approved canonical monster. Keep the photographed product unchanged and photographic; lock the monster's identity while adapting only its pose for one clear interaction. Text and no-text versions must use independent compositions.

This branch never requires desktop-runner preflight. If the user selected both fusion poster and runnable pet, continue the poster branch even when the runner is missing or installation is declined.

## Runnable desktop pet

Read `references/desktop-pet-workflow.md`, `references/desktop-pet-environment.md`, `references/mixed-media-style-guide.md`, and `references/desktop-pet-pack.md`.

- For an approved `flavor-monster`, run `scripts/check_desktop_pet_environment.py --json --required-schema 3` only now, before motion generation.
- For an explicit `source-faithful` request, first complete its three-candidate identity workflow and obtain explicit canonical-identity approval; then run the same environment gate before motion generation. Source-faithful remains schema v2 and flavor-monster uses schema v3.
- If preflight reports missing or outdated components, explain the exact plan and request consent immediately before installation or upgrade. Never silently install or replace software, bypass operating-system warnings, or enable launch-at-login.
- Continue only after preflight reports `ready`. Then create the mode-specific motion set, request motion approval, and only after approval build and validate the importable pack and delivery folder.

For schema-v1 migration, preserve the original pack, create a new v2 draft, add the four missing states, and require fresh motion approval. Never overwrite or silently activate the v1 pack.

White backgrounds are for identity and motion review only. Runtime animation files require real alpha transparency.

## Output boundary

- Never describe exploratory image-model output as a finished pet pack.
- Do not fabricate file paths, validation results, or runnable installers.
- If visual generation is unavailable, return the staged prompt packet and state which artifacts remain ungenerated.
- Do not save generation prompts as standalone project documents unless the user explicitly asks for prompt files.
- Treat official-looking marks, private-study-only cutouts, and `quality: avoid-default` records as analysis-only.
- Preserve user files and unrelated working-tree changes.

Human visual approval is mandatory at both desktop-pet gates; automated validation cannot replace it.
