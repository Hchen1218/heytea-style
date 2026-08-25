# Desktop Pet Workflow

Read this reference only for desktop-pet requests.

## Outcome

Turn one photographed subject into a quiet desktop companion that is recognizable at small size, feels alive without interrupting work, and can be imported into the bundled runner.

This mode is a full illustration conversion. Unlike poster mode, it does not preserve photographic texture.

## Stage 0: Environment gate

Before analyzing the photo, follow `desktop-pet-environment.md` and run the read-only preflight. Continue only when the runner is installed or the user has explicitly chosen a static-concept-only path.

If anything is missing, show one concrete repair plan and ask for installation consent. After approval, automatically fill only the missing components, rerun preflight, and stop if it still does not report `ready`. This system gate is separate from the later character and motion approval gates.

## Stage 1: Subject gate

Classify the input before prompt writing:

- **No usable subject**: stop. Ask for a new image with one sharp, well-lit subject and a readable outline.
- **Several independent subjects**: show short numbered descriptions, optionally with crop callouts when the image tool supports them, and ask which one to use.
- **One subject**: proceed without another question.
- **Container plus contents**: use the visible unit as one character by default. A cup and its drink, bowl and food, or bottle and water share one silhouette.

Record a compact identity brief:

- silhouette and orientation;
- one to three source colors;
- two to four must-preserve features;
- parts that may be simplified;
- a subject-specific motion idea.

## Stage 2: Candidate board

Before prompt writing, inspect all three model-facing boards listed in `mixed-media-style-guide.md`. Use them together: object/material construction, action anatomy, and thin-stroke anatomy are separate controls.

### Two-pass candidate construction

For mixed-media drinks, soft foods, or any retry where the material reference is correct but the generated outline remains clean, separate line and color:

1. **Line skeleton**: generate the three candidates in black on warm white with no color or shading. Borrow only line anatomy from poster-mode `figures/full-poses/*` and `lettering/strokes/*`. Every stroke—not merely the overall contour—must visibly meander with shallow waves, drifting curvature, and pressure wobble. Use gaps, overshoots, retracing, and bad joins as secondary traits. Require structural asymmetry in rim, opening, walls, lid, base, and perspective. Reject ruler-straight walls, rims, limbs, and facial dashes even when they are broken into fragments.
2. **Locked color pass**: use the accepted skeleton as the edit target. Preserve every black stroke, gap, face, limb, and position exactly. Add color behind the line only. Use the dry-media/wavy-line board to assign colored pencil, childlike wax crayon, graphite, and optional pale wash to different material regions. Do not redraw, complete, smooth, or repair the line while coloring, and do not apply one uniform color texture across the full body.

Keep both review artifacts. The colored board is not allowed to bypass a failed line skeleton.

Generate one review board with three full-body candidates on white or warm white. All three must depict the same subject at the same scale, in the same neutral front-facing stance, with arms relaxed and feet on one shared ground anchor. A candidate board compares identity design, not animation poses.

Keep constant:

- outer silhouette and major internal divisions;
- source palette;
- recognizable container, topping, label-free package, or ingredient details;
- thin-to-medium hesitant black line structure with occasional retracing, open joins, and overshoot;
- structurally crooked geometry rather than a clean template with a wobble filter;
- source-appropriate material zoning; for drinks and soft foods, combine light colored-pencil scumbling, broad childlike wax-crayon marks, paper-white clear areas, and only optional pale smears rather than one uniform treatment.

Vary only:

- placement and size of the minimal crooked face;
- short arm and leg proportions;
- structural crookedness and stable temperament: quiet, curious, or gently clumsy, expressed without changing pose.

Do not use waving, walking, leaning, jumping, sleeping, or other action differences to create the illusion of three concepts. If removing the pose would make the candidates indistinguishable, the board has failed.

The subject is the body. Do not put it in an animal costume or add detailed clothing. Avoid uniform heavy outlines, smooth digital gradients, solid textureless fills, polished vector outlines, sticker borders, kawaii rendering, glossy 3D shading, realistic faces, text, watermarks, or official brand marks. Cuteness should come from awkward proportion, material marks, and a readable action rather than large eyes.

Ask the user to choose candidate 1, 2, or 3, or request a focused revision. Do not infer approval from silence.

Before presenting the board, perform a limb inventory on every candidate. Unless the approved concept explicitly calls for another anatomy, each candidate must show exactly two arms and two clearly visible legs. Broken-line style may create gaps inside a limb, but it must not erase the limb or merge it into the body/color mass. Fix only the affected candidate before asking for approval.

### Pose-only consolidation

If a presented board already has one shared identity and differs only through pose:

1. State that these are motion sketches, not valid identity variants; do not force a meaningless three-way choice.
2. Use the most neutral standing pose to create one canonical master with fixed cup geometry, face placement, limb count and proportions, line behavior, media zoning, and foot anchor.
3. Treat the other poses only as motion references. A raised arm may inform `wave`; a tilt may inform `happy` or `land`.
4. Obtain explicit approval of the consolidated identity before motion generation. Keep the canonical master as the sole identity reference for every action.

## Stage 3: Motion design

After character approval, make a consistent action model sheet. Use the approved candidate as the only identity reference.

Before drawing actions, record a compact canonical lock from the master: face coordinates, two-arm/two-leg inventory, limb lengths, cup aspect ratio, lid offset, four color/material zones, foot anchor, and the characteristic amplitude of line waviness. Pose references may change gesture but never override this lock.

Required actions:

| State | Visual purpose | Runtime trigger | Art expectation |
|---|---|---|---|
| `idle` | Breathing and occasional blink | Default loop | 2–4 key frames; runner adds subtle bob |
| `walk` | Short floor movement | Autonomous movement | 4–6 frames; faces right and may be mirrored |
| `rest` | Sitting or sleeping | Long inactivity | 3–4 frames; quiet pose with optional Zzz overlay |
| `happy` | Acknowledges affection | Single click | 3–5 frames; readable at small size |
| `drag` | Reacts to being held | Pointer drag | 2–3 frames; tucked limbs, no distress |
| `land` | Recovers after release | Drag release | 3–5 frames; squash then settle |
| `wave` | Rare autonomous greeting | Low-frequency ambient action | 3–5 frames; one short limb gesture |
| `signature` | Expresses subject identity | Low-frequency ambient action | 3–6 frames; bubbles, wobble, crumbs, roll, steam, or another subject-specific verb |
| `curious` | Looks around | Cursor-near or ambient | 3–4 frames; small eye/head shift without body drift |
| `stretch` | Releases tension | Ambient | 4–5 frames; full readable stretch and settle |
| `tiptoe` | Peers upward | Cursor-near or ambient | 3–4 frames; intentional vertical lift without lateral drift |
| `play` | Entertains itself | Ambient | 4–6 frames; interacts with a subject-specific internal feature |

Optional runtime-extension actions stay compatible with schema v2:

| State | Visual purpose | Runtime trigger | Art expectation |
|---|---|---|---|
| `fall` | Bridges a high drag release into `land` | Release above the floor | 3–5 looping frames; held/tucked pose → airborne pose → landing anticipation; no floor line |
| `touch` | Gently acknowledges a nearby cursor | End of one bounded cursor chase | 4–6 frames; neutral → reach toward one side → retract → neutral; mirrorable |

When replacing earlier actions, the newest explicitly approved action family is the style baseline. Match its line weight, waviness, media zoning, opacity, face system, and limb construction; do not average old and new styles together. For transition-linked groups (`drag → fall → land`, `walk → touch → walk`), review adjacent end frames side by side and make each boundary share a compatible silhouette.

Use handcrafted/model-generated frames for silhouette-changing poses. Let the runtime supply mirroring, translation, subtle breathing, light sway, heart/Zzz particles, and squash/stretch.

## Stage 4: Motion approval

Provide both:

- a labeled contact sheet showing every state at one consistent scale;
- a looping preview that plays all states without hiding identity drift.

Review before asking for approval:

1. Does every state still look like the chosen candidate?
2. Are the face, limbs, palette, line weight, and object features stable?
3. Do the feet share a consistent ground anchor?
4. Are loops free of obvious jumps or clipped pixels?
5. Are actions readable around a 120–140 px default desktop size?
6. Does the character remain quiet rather than hyperactive or disruptive?

If one state fails, regenerate that state only. Do not rerun the full set unless the identity system itself is wrong.

Ask for explicit motion approval. Package only after approval.

## Generation prompt frame

Use the uploaded photo and approved candidate as references. Adapt details to the subject rather than copying this wording mechanically:

```text
Create a coherent desktop-pet animation strip for the approved object character.
Preserve exactly the same silhouette, one-to-three-color palette, minimal crooked face,
short limbs, structurally crooked hand-redrawn geometry, hesitant mixed-weight pen,
and source-appropriate hand color. For drinks and soft foods preserve the approved media
zoning: light colored pencil, broad childlike wax crayon, paper-white clear areas, and
only optional pale smears in every frame.
The subject itself remains the body. Transparent background, no white rectangle, no text,
no logo, no watermark, no costume, no new accessories, no polished vector line.

Action: [state and one clear verb].
Frames: [count], laid out left to right on a single horizontal strip.
Keep one fixed canvas per frame and one fixed foot anchor. Do not crop motion.
```

Generate each state as a separate strip so a failed action can be replaced without changing the others.

Every generated cell must have a clear empty gutter. No limb, color patch, motion mark, floor line, or neighboring character may cross the cell boundary. After conversion, build `frame-audit.png` on a contrasting dark background and inspect every frame—not only the representative contact-sheet frame. Detached side marks, partial neighboring limbs, pale rectangles, and checkerboard residue fail the motion gate.

Ambient actions should remain readable for roughly 1.5–3 seconds at runtime. Prefer 2–4 FPS for hand-drawn key poses; a higher FPS does not create smoothness when the strip contains only four to six distinct drawings. The first and last pose should settle toward the same neutral identity so transitions do not snap.

## Default behavior personality

The bundled runner implements quiet companionship:

- idle is dominant;
- walking is short and infrequent;
- wave and signature actions are rare;
- rest begins after prolonged inactivity;
- click and drag responses preempt ambient actions;
- no hunger, feeding, chat, sound, cursor theft, window manipulation, or prank behavior.
- stable idle never continuously redraws or moves the window; micro-idle plays every 5–9 seconds;
- balanced ambient episodes begin every 8–15 seconds, while walk has a separate 90-second cooldown;
- cursor proximity may trigger one bounded interaction episode: move toward the cursor by at most 80 px, play `touch`, then return to the exact pre-trigger x position. Lock the target at trigger time; never continuously follow, capture input, or request accessibility permissions.
- releasing a dragged pet above the floor plays `fall` while the window descends monotonically, then `land`; never snap directly to the ground.
