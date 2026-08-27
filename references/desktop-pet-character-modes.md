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

The photograph supplies flavor DNA rather than a body template. Extract:

- one to three identifying colors;
- one or two ingredient/material cues, such as fruit cubes, pearls, foam, bubbles, crumbs, glaze, leaves, or transparency;
- one source-specific motion verb;
- optional structural memory that can become one small biological feature, such as a leaf-horn, translucent belly patch, spotted skin, tail tip, or head tuft.

### Character identity

- The first impression must be an independent creature or monster; source recognition comes second through flavor DNA.
- Use a biological silhouette such as a soft blob, squat hatchling, sprout creature, lopsided nugget, or another simple organism. Do not retain a complete cup, bowl, bottle, wrapper, lid, rim, straw, or container-wall silhouette.
- Convert ingredients into anatomy or markings rather than leaving them as contents sitting at the bottom of a vessel.
- Use one intentional oddity—uneven horns, one drooping ear, an off-center tuft, a short tail, or another restrained asymmetry. Avoid stacking many mascot traits.
- Cuteness comes from awkward proportions, tiny facial marks, short clumsy appendages, and temperament—not large eyes or generic chibi styling.
- Candidate differences may vary biological silhouette, face system, appendage proportions, the placement of source-DNA features, and stable temperament. All candidates still use the same source DNA, neutral front-facing stance, scale, and ground anchor.

### Action identity

- Use anatomy-led secondary motion: leaf-horns, ears, tuft, tail, belly markings, or ingredient features react before or after the whole body.
- Define 6–10 complete schema-v3 behaviors around the approved anatomy rather than filling a fixed action-name checklist.
- Include bindings for awake idle, sleep, click, pointer encounter, drag, release, and at least one ambient behavior.
- Sleep must visibly enter, persist in a loop, and wake through an exit; exploration, cursor encounter, held, and drop recovery may also use explicit phases.
- Give each behavior enough amplitude and internal progression to read as one story. Prefer fewer substantial behaviors over many tiny interchangeable gestures.
- Flavor events such as a fruit-cube hiccup, one bubble, color ripple, or leaf-ear shake should arise from anatomy or an internal feature, not a generic prop.
- Drag, fall, impact, rebound, and settle must preserve the monster silhouette and connect physically; loose ears, horns, tufts, and tails may lag or settle, but limb inventory must remain stable.

## Shared production contract

Both character modes use:

- the same environment preflight and installed shared runner;
- the same black-skeleton then locked-color candidate process when mixed-media construction needs it;
- the same explicit character-approval and motion-approval gates;
- the same 120–140 px readability target, transparent runtime strips, version-aware builder and validator, and delivery folder.

The public formats remain intentionally separate: `source-faithful` uses schema v2 with twelve required actions and optional `fall` / `touch`; `flavor-monster` uses schema v3 with 6–10 reachable behaviors and explicit phases. Both compile to one internal runtime model. Do not migrate existing v2 packs or duplicate the Electron runtime.
