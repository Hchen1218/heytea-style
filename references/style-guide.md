# Style Guide

This guide captures the reusable visual structure from the provided reference set without copying official brand assets.

## Style Diagnosis

The look is not full image-to-cartoon conversion. It is a staged product poster:

- Real object anchor: a drink cup, tea bag, dessert, ingredient, or daily-life object remains photographic.
- White field: the background is nearly empty and gives the drawing room to breathe.
- Doodle intervention: primitive black-line micro workers explain, touch, carry, taste, or imagine around the object. They are not cute cartoon characters.
- Handwritten copy: main titles feel like rough black brush-marker sign lettering; small notes feel like thin pen product notes.
- Small brand-like mark: references often include a bottom icon, but this skill should not reproduce official HEYTEA marks by default.

## Template Selection

Do not treat text as a simple on/off layer. The typography-led version and the no-text version are two independent poster systems with different composition priorities and action density.

Before generating, choose one:

- `带字版`: typography is the first visual priority. The object and micro worker support the crooked title.
- `无字版`: the object-and-action story is the first visual priority. No text appears anywhere.
- `两套都出（推荐）`: create two independent concepts, one from each template. Do not reuse the same layout and merely remove or add text.

If the user does not choose, default to `两套都出（推荐）`.

## Composition Recipes

### Recipe A: Product Anchor

Use when the input is a cup, food, package, plant, bottle, book, or object with a clear silhouette.

- Put the real object slightly below center or slightly off-center.
- Keep the object at about 25 percent to 45 percent of canvas height.
- Add one doodle action close to the object, such as a tiny person pouring, climbing, carrying, inspecting, or tasting.
- Put the title in the upper-left or mid-left white space.

### Recipe B: Ordinary Object as Poster

Use when the object is not food or drink, such as keys, shoes, a notebook, a lamp, or a bag.

- Do not force it to become a drink product.
- Treat it like a quiet daily-life artifact.
- Add doodles that reveal the object's personality: tiny movers for keys, a reader for books, a traveler for shoes, a cleaner for a cup.
- Use copy that names the feeling, not a fake product spec.

### Recipe C: Busy Photo Recovery

Use when the photo has a complex room, street, desk, or crowd background.

- Isolate the strongest object.
- Replace or heavily simplify the background into white or warm off-white.
- Keep the original object's surface texture and shadow.
- Add doodles only after the visual field is quiet.

## Two Independent Templates

### Template A: Typography-Led Poster

Use when the user chooses `带字版`, or when the concept depends on a memorable Chinese phrase.

For accurate lettering, follow `references/lettering-guide.md`. The preferred execution is not a single all-in-one image prompt. Generate a clean poster base first, then generate or place the handwritten title as a separate black title layer. Use all-in-one generation only for quick drafts.

Composition:

- Make the rough Chinese title the first visual signal, usually in the upper-left or along the left side.
- Give the title a large block of white space. It should feel intentionally awkward and hand-painted, not like a neat caption.
- Place the real object smaller, usually middle-lower, lower-right, or slightly below center. The object supports the title instead of competing with it.
- Keep the micro worker small and quiet. It can point, sprinkle, hold, inspect, or perform one simple action, but it must not pull attention away from the title.
- Use almost no supporting props. Avoid decorative lemon slices, stickers, repeated bubbles, and busy action marks near the title.

Lettering:

- Use rough black marker or blunt brush lettering.
- The characters should be crooked, childlike, uneven, and slightly badly spaced.
- Strokes should have irregular pressure: some parts heavy and blocky, some parts thin or broken.
- Prefer vertical one-column or two-column Chinese title blocks, but never a perfect 2x2 grid. Four-character titles should be two loose staggered vertical columns.
- Avoid clean fonts, rounded cute handwriting, neat calligraphy, print-like sans-serif text, and balanced commercial typography.

### Template B: No-Text Narrative Poster

Use when the user chooses `无字版`, or when image-model text accuracy would distract from the poster.

Composition:

- Forbid all text, letters, numbers, captions, labels, watermarks, and random glyphs.
- Do not reserve a title block. Fill the poster through object placement, action path, and negative space.
- Let the real object and micro worker create a complete tiny scene: pouring, pushing, climbing, dragging, washing, throwing, fishing, repairing, or carrying.
- The micro worker can be slightly larger and more active than in Template A, because there is no title competing for attention.
- Supporting elements are allowed only when they clarify action: one ladder, bucket, bag, arrow, thought bubble, liquid arc, ground line, or two to three drops.
- Keep the total number of doodle elements low. The scene should feel like a quiet object theater, not a sticker collage.

## Figure Language

The reference figures are not generic cute doodle people. Treat them as primitive micro workers or tiny product operators. They are functional marks that explain scale, action, and use.

Use this figure system:

- scale: usually 8 percent to 18 percent of the real object height;
- head: blank lumpy circle-ish head built from two to four short broken strokes, almost always no eyes, no mouth, no expression;
- body: short tube body or irregular U-shaped work suit made from open segments, not a chibi body;
- limbs: stiff segmented arms, blocky paddle ends, and short bent dash feet; avoid round mitten hands and oval feet;
- line: black, uneven, stuttering, marker-like, with blunt ends and bad joins, not smooth vector;
- fill: mostly empty outline; avoid filled hair blocks except when the user explicitly asks for a logo-like drinking-head mark;
- pose: practical actions, such as pouring, lifting, pushing, dragging, climbing, sweeping, inspecting, carrying, fishing, throwing, or pointing.

Line anatomy:

- Build figures from short imperfect stroke segments, not one clean continuous outline.
- Use visible blunt ends, tiny gaps, overshoots, hard bends, and bad joins.
- Keep curves slightly angular or kinked; avoid perfect circles, smooth shoulders, smooth hands, and polished icon contours.
- Large figures are risky because models smooth the outline. If using a large figure, break the body into open strokes, straight-ish arms, blocky paddle ends, and prop lines instead of one closed mascot silhouette.
- Prefer ladder, bucket, bag, motion arc, ground line, and tool props when the composition needs bigger visual mass. These props preserve the reference's crude line quality better than a large round character.

Good supporting marks:

- rough liquid arcs, two or three drops, steam puffs, arrows, thought bubbles, ladders, single-stroke ground lines;
- simple geometric props drawn badly on purpose: cubes, bags, boats, buckets, cups, handles;
- one action line that connects the figure to the real object.

Avoid:

- polished vector icons;
- kawaii stickers;
- dense comic panels;
- fully rendered characters;
- realistic faces, facial expressions, detailed clothes, hair, or fingers;
- multiple cute mascots competing with the real object;
- colored doodles unless the object itself needs a matching accent;
- imitating the official HEYTEA logo or mascot;
- large smooth closed-outline mascot bodies with perfect circular heads, round mitten hands, and oval feet.

### Micro-Worker Action Grammar

The worker is not decoration. It should make the real object feel like a tool, terrain, ingredient, machine, or stage.

Use one clear action verb before drawing:

- pour: worker tips a kettle, bottle, bag, or cup; use one liquid arc and two or three drops;
- throw: worker tosses cubes, fruit, beans, ice, or toppings; use one broken motion arc;
- push or drag: worker braces against a large ingredient or pulls a stretchy element;
- climb or repair: worker uses a ladder, bucket, rope, or small tool near the object;
- wash or mix: worker stands near a bucket or bowl and performs one repetitive task;
- inspect or point: worker is small and restrained for typography-led posters;
- imagine: back-view worker with one to three rough thought bubbles.

For `带字版`, the action should stay quiet and serve the title. For `无字版`, the action can become the main story. Do not add more workers to compensate for a weak idea; choose a stronger action verb.

## Lettering Pattern

Keep in-image text short because image models still make text mistakes.

There are two lettering modes:

1. Main title lettering: rough black brush-marker Chinese, heavy ink, angular and uneven, with thick-thin stroke variation. It should look like primitive hand-painted sign lettering or awkward childlike calligraphy. Prefer vertical one-column or two-column layouts in the upper-left white space. Do not use clean sans-serif, rounded cute fonts, neat handwriting, or UI typography.
2. Small note lettering: thin black pen, loose spacing, packaging-note feeling. Use only for small product notes or subtitles, and never let it compete with the real object.

Best main-title patterns:

- `把今天装进口袋`
- `慢慢喝一口`
- `小小补给站`
- `今天也要松一松`
- `一杯安静的甜`

For four-character titles, prefer two vertical columns:

```text
酸  降
甜  温
```

or:

```text
柠  冰
檬  咖
```

Subtitle patterns:

- `给忙乱的一点空白`
- `真实物件 + 小人涂鸦`
- `生活里的轻轻一口`
- `不用很满，也很好`

If the user provides product or object details, write more specifically. If Chinese text must be exact, recommend adding it as post-edit text if generation mangles it.

## Private Cutout Asset Workflow

When `private-assets/reference-cutouts/asset-index.json` exists, use it before writing prompts. These files are local private references extracted from the user's reference set. Use them to improve fidelity on line weight, wobble, figure proportions, gesture, and handwritten rhythm. Do not package them into a public skill release.

Asset selection rules:

- Prefer records with `"quality": "primary"`.
- Use `lettering/title-blocks/*` only for `带字版`. These are the main crooked title rhythm references.
- Use `lettering/glyphs/*` and `lettering/strokes/*` for title construction sheets, especially when the output looks too font-like.
- Use `lettering/notes/*` only for secondary note style, not as the main title style.
- Use `figures/full-poses/*` for micro-worker pose and action references.
- Use `figures/action-parts/*` only when the action needs a prop or motion mark such as an arrow, ladder, bucket, liquid arc, cube path, thought bubble, or ground line.
- Do not use lettering assets in `无字版`.
- Treat records with `"quality": "avoid-default"` or `"copyright_scope": "private-study-only"` as analysis-only. Do not use logo-like marks as default generation assets.
- Do not reproduce official logos, official mascot marks, or source-file text as final claims.

Recommended figure matches:

- pour, refill, steaming: `worker_kettle_pour`
- throwing, dropping, tossing: `worker_throw_cube`
- thinking, choosing, imagining: `worker_thinking_bubbles`
- reading, opening, quiet large figure: `worker_large_reading`
- holding, carrying, inspecting: `worker_carry_basket`
- pulling, stretching, dragging: `worker_pull_cheese`
- cleaning, mixing, washing, bucket work: `worker_cleaning_bucket`
- ladder or bucket scene: `ladder_bucket_props`
- directional motion: `rough_arrow`
- liquid arc, steam, drops: `action_liquid_arc_pour`
- title staging ground line: `ground_line_large_eater`

Template A asset use:

- Select one primary `lettering/title-blocks/*` asset as the typography rhythm reference.
- Select two to six `lettering/glyphs/*` or `lettering/strokes/*` assets to build the title construction sheet.
- Select zero or one restrained primary `figures/full-poses/*` asset only if it clarifies the object story.
- If exact Chinese text matters, make the image generation leave a clean title area, build a title construction sheet, then add the final text in a separate title layer. Do not keep trying all-in-one image prompts.

Template B asset use:

- Select one primary `figures/full-poses/*` asset that matches the action story.
- Optionally select one `figures/action-parts/*` asset.
- Do not select lettering assets and do not reserve title space.

When local private assets exist, list selected reference assets by path and purpose. If they do not exist, use the style rules and prompt templates without pretending that private cutouts are available.

## Prompt Templates

Use one of these templates. For `两套都出（推荐）`, use both templates separately.

### Template A Prompt: 带字版

Prefer the two prompts below.

#### Pass 1: Poster Base

```text
Use the uploaded image as the source photo. Create a vertical 1024x1536 poster base inspired by playful minimal beverage product posters.

Goal:
Preserve the main photographed object as a real object with its original texture, material, shape, and natural shadow. Do not convert the whole image into a cartoon.

Layout:
Clean white or soft off-white background, generous negative space, portrait poster composition. This is the typography-led version, but do not render the title yet. Reserve a large empty title field in the upper-left or left side for a later black handwritten Chinese title layer. Place the real object [placement], smaller than the empty title field, about [scale] of canvas height, usually middle-lower or lower-right.

Doodle overlay:
Add one small primitive black-line micro worker near the object only if useful. The figure should look like a tiny product operator drawn with an uneven black marker: blank lumpy circle-ish head made from short broken strokes, no face, short open-segment tube body, stiff segmented arms, blocky paddle ends, short bent dash feet, naive proportions, no detailed clothes, no hair, no cute expression. Show a restrained action: [doodle action]. Keep the title area empty.

Constraints:
No title, no Chinese characters, no English letters, no numbers, no captions, no logo, no official HEYTEA mark, no watermark, no dense decorations, no comic panel layout, no full cartoon conversion, no cute mascot, no realistic face. Preserve the real object and edit only the background, object placement, optional micro worker, and minimal action marks.
```

#### Pass 2: Title Construction Reference Sheet

Before generating the title layer, build a private reference sheet when local cutouts exist. The default output is model-facing: no English labels and no target title rendered as a system font.

```bash
python scripts/build_title_reference_sheet.py \
  --title "[title]" \
  --out private-assets/reference-cutouts/title_reference_sheet_[slug].png \
  --title-ref [title-block asset name]
```

Use `lettering/title-blocks/*` for title rhythm and `lettering/glyphs/*` / `lettering/strokes/*` for the malformed Chinese glyph anatomy. This sheet is the control image for the title layer. Use `--human-labels` only for inspection, not as the image-model reference.

#### Pass 3: Title Layer

```text
Create only a black handwritten Chinese title layer on plain white or transparent background.

Text:
"[title]"

Layout:
Use [title layout]. For a four-character title, use two loose staggered vertical columns, not a perfect 2x2 grid.

Reference assets:
Use [title construction sheet path] as the primary reference. Match the crooked childlike marker rhythm, malformed glyph skeletons, uneven scale, blunt broken stroke ends, awkward spacing, off-grid placement, non-parallel strokes, collapsed radicals, ugly joins, and primitive hand-painted feel.

Style:
The Chinese characters should look like an untrained child wrote them with a blunt black marker: flat black ink, independent wobbly strokes, bad joins, uneven character boxes, non-parallel horizontals, crooked verticals, imperfect but readable Chinese. Not brush calligraphy, not an elegant poster font, not sans-serif, not rounded cute handwriting, not a clean computer font, not a dry-brush art effect.

Constraints:
Only the title. No object, no doodle worker, no logo, no watermark, no pinyin, no English, no numbers, no extra glyphs.
```

#### Draft-Only All-In-One Prompt

Use this only when the user wants a quick rough draft and accepts text instability.

```text
Use the uploaded image as the source photo. Create a vertical 1024x1536 poster inspired by playful minimal beverage product posters.

Goal:
Preserve the main photographed object as a real object with its original texture, material, shape, and natural shadow. Do not convert the whole image into a cartoon.

Reference assets:
Use selected local private cutouts as style references: [title construction sheet path] for rough crooked title glyph skeleton and stroke rhythm, and [optional figure reference path] for primitive micro-worker proportions and gesture. Use them as line-style and pose references, not as official brand assets. This all-in-one route is draft-only; for fidelity, generate the title layer separately.

Layout:
Clean white or soft off-white background, generous negative space, portrait poster composition. This is the typography-led version. Make the rough Chinese title the first visual priority in the upper-left or left side. Place the real object [placement], smaller than the title block, about [scale] of canvas height, usually middle-lower or lower-right.

Doodle overlay:
Add one small primitive black-line micro worker near the object. The figure should look like a tiny product operator drawn with a thick uneven black marker: blank lumpy circle-ish head made from separate blunt strokes, no face, short open-segment tube body, stiff segmented arms, blocky paddle ends, short bent dash feet, naive proportions, no detailed clothes, no hair, no cute expression. Show a restrained action: [doodle action]. Use no more than one supporting action mark.

Text:
Add a rough crooked childlike Chinese marker title: "[title]". Prefer vertical one-column or two loose staggered columns. The characters should not form a perfect grid. They should be heavy black, angular, uneven, badly spaced, primitive, and hand-painted, like a child wrote with a blunt black marker. Use independent wobbly strokes, bad joins, blunt broken ends, non-parallel horizontals, crooked verticals, and uneven character boxes. Not a clean computer font, not rounded, not cute, not neat handwriting, not elegant calligraphy, not sans-serif, not dry-brush art. Optional small note: "[subtitle]" in thin loose pen style only if needed.

Constraints:
No official HEYTEA logo, no watermark, no fake brand mark, no dense decorations, no comic panel layout, no full cartoon conversion, no extra random text, no cute mascot, no realistic face. Preserve the real object and edit only the background, lettering, small primitive micro worker, and minimal action marks.
```

### Template B Prompt: 无字版

```text
Use the uploaded image as the source photo. Create a vertical 1024x1536 poster inspired by playful minimal beverage product posters.

Goal:
Preserve the main photographed object as a real object with its original texture, material, shape, and natural shadow. Do not convert the whole image into a cartoon.

Reference assets:
Use selected local private cutouts as style references: [figures/full-poses reference path] for primitive micro-worker proportions and action pose, and [optional figures/action-parts reference path] for action marks. Do not use any lettering reference for this version.

Layout:
Clean white or soft off-white background, generous negative space, portrait poster composition. This is the no-text narrative version. Do not reserve a title area. Place the real object [placement] and build the composition around the action story. Keep the object about [scale] of canvas height.

Doodle overlay:
Add one primitive black-line micro worker that creates a complete tiny action scene with the object: [doodle action]. The figure should look like a tiny product operator drawn with a thick uneven black marker: blank lumpy circle-ish head made from separate blunt strokes, no face, short open-segment tube body, stiff segmented arms, blocky paddle ends, short bent dash feet, naive proportions, no detailed clothes, no hair, no cute expression. The action can be clearer and slightly larger than the typography-led version, but the outline must stay broken and crude. Add only action-supporting props from this set if useful: one ladder, one bucket, one bag, one arrow, one thought bubble, one liquid arc, one ground line, or two to three drops.

Text constraints:
No text anywhere. No Chinese characters, no English letters, no numbers, no labels, no captions, no logo text, no random glyphs, no watermark. If the source object has a real product label, preserve it only if it is part of the photographed object; do not invent new text.

Constraints:
No official HEYTEA logo, no fake brand mark, no dense decorations, no comic panel layout, no full cartoon conversion, no stickers, no cute mascot, no realistic face. Preserve the real object and edit only the background, primitive micro worker, and action-supporting marks.
```

## Prompt Fill-In Guide

- `[placement]`: for Template A use middle-lower, lower-right, or slightly below center; for Template B use center-left, center-right, lower-center, or any placement that supports the action story.
- `[scale]`: 25 percent to 45 percent.
- `[doodle action]`: for Template A use a restrained action such as pointing, sprinkling, inspecting, holding, or a short pour. For Template B use a fuller action such as pouring, pushing, carrying, climbing, washing, dragging, lifting, fishing, throwing, repairing, or using the object like equipment.
- `[title]`: 4 to 8 Chinese characters when possible; use two vertical columns for four-character titles.
- `[subtitle]`: 6 to 14 Chinese characters; omit if unnecessary.

## Object-Specific Example: Iced Coffee and Lemonade

For a photo with an iced drink cup and lemonade bottle, avoid making both objects equally important. Use the cup as the main real object and the bottle as a supporting prop.

Template A direction:

```text
Preserve the iced drink cup and lemonade bottle as real photographic objects, but let the rough title dominate the poster. Place the title in large crooked black two-column Chinese lettering in the upper-left:
酸  降
甜  温

Place the cup and bottle smaller in the lower-right or lower-middle. Add only one small primitive micro worker doing a restrained pour or pointing action. Do not add extra decorative lemon slices.
```

Template B direction:

```text
Preserve the iced drink cup as the main real photographic object and keep the lemonade bottle as a supporting prop. No text anywhere. Do not reserve a title area.

Build a tiny action scene: one primitive micro worker stands on the bottle cap or shoulder and clumsily tips the bottle toward the cup. Draw one rough curved line showing liquid falling into the cup, plus two small drops. The action should carry the meaning without any words.
```

## Revision Prompts

Too cartoonish:

```text
Revise the image by preserving the real photographed object exactly. Change only the doodle overlays and background. The object should remain photographic, not illustrated.
```

Too cluttered:

```text
Reduce the doodles by half. Keep only one tiny black line character and one simple action mark. Increase white negative space.
```

Text is wrong:

```text
Remove the generated text and leave clean white space in the upper-left for manual text overlay. Keep the object and doodles unchanged.
```

No-text version leaked text:

```text
Remove every invented character, letter, number, caption, label, and glyph from the poster. Do not leave a title area. Keep the object-and-action composition intact.
```

Object changed too much:

```text
Restore the source object's original silhouette, material, color, and shadow. Keep only the white poster background and black childlike doodle interaction.
```

Not enough brand-poster feeling:

```text
Make the layout feel more like a quiet premium drink product poster: more white space, fewer elements, stronger real-object anchor, one short handwritten Chinese title, and black doodles that interact with the object.
```
