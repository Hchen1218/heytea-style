# Desktop Pet Workflow

Read this reference only for desktop-pet requests.

## Outcome

Turn one photographed subject into a quiet desktop companion in the user-selected character mode, recognizable at small size, alive without interrupting work, and importable into the bundled runner.

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

- one to three source colors;
- subject orientation and material regions;
- two to four source features that can identify the result;
- parts that may be simplified or translated;
- a subject-specific motion idea.

## Stage 1.5: Character-mode gate

Read `desktop-pet-character-modes.md`. If the user has not already chosen a mode, ask whether they want:

1. `source-faithful`（写实卡通桌宠）—the photographed subject remains the character body; or
2. `flavor-monster`（风味小怪兽桌宠）—the photograph supplies flavor DNA for a newly designed creature.

Stop before candidate generation until the mode is explicit. Do not recommend, default, or infer one from the subject category. When the request already says 写实卡通、保留原物形态、小怪兽, or otherwise makes the choice unambiguous, record it and continue without asking again.

Extend the identity brief according to the selected mode:

- `source-faithful`: record outer silhouette, major internal divisions, and must-preserve object/container details.
- `flavor-monster`: record color DNA, one or two ingredient/material cues, one motion verb, and the biological feature each cue may become. Do not lock the source container silhouette.

## Stage 2: Candidate board

Before prompt writing, inspect all three model-facing boards listed in `mixed-media-style-guide.md`. Use them together: object/material construction, action anatomy, and thin-stroke anatomy are separate controls.

### Two-pass candidate construction

For mixed-media drinks, soft foods, or any retry where the material reference is correct but the generated outline remains clean, separate line and color:

1. **Line skeleton**: generate the three candidates in black on warm white with no color or shading. Borrow only line anatomy from poster-mode `figures/full-poses/*` and `lettering/strokes/*`. Every stroke—not merely the overall contour—must visibly meander with shallow waves, drifting curvature, and pressure wobble. Use gaps, overshoots, retracing, and bad joins as secondary traits. Require structural asymmetry in rim, opening, walls, lid, base, and perspective. Reject ruler-straight walls, rims, limbs, and facial dashes even when they are broken into fragments.
2. **Locked color pass**: use the accepted skeleton as the edit target. Preserve every black stroke, gap, face, limb, and position exactly. Add color behind the line only. Use the dry-media/wavy-line board to assign colored pencil, childlike wax crayon, graphite, and optional pale wash to different material regions. Do not redraw, complete, smooth, or repair the line while coloring, and do not apply one uniform color texture across the full body.

Keep both review artifacts. The colored board is not allowed to bypass a failed line skeleton.

Generate one review board with three full-body candidates on white or warm white. All three must use the same source or source DNA at the same scale, in the same neutral front-facing stance, with arms relaxed and feet on one shared ground anchor. A candidate board compares identity design, not animation poses.

Keep constant in both modes:

- source palette;
- thin-to-medium hesitant black line structure with occasional retracing, open joins, and overshoot;
- structurally crooked geometry rather than a clean template with a wobble filter;
- source-appropriate material zoning; for drinks and soft foods, combine light colored-pencil scumbling, broad childlike wax-crayon marks, paper-white clear areas, and only optional pale smears rather than one uniform treatment.

For `source-faithful`, also keep the source outer silhouette, major internal divisions, and recognizable container, topping, label-free package, or ingredient details. Vary only:

- placement and size of the minimal crooked face;
- short arm and leg proportions;
- structural crookedness and stable temperament: quiet, curious, or gently clumsy, expressed without changing pose.

For `flavor-monster`, keep the color, ingredient/material, and motion DNA rather than the photographed container silhouette. Vary only:

- a simple biological body archetype and its restrained asymmetry;
- minimal face system and short appendage proportions;
- where source-DNA cues become horns, ears, tuft, tail, belly patch, skin marking, or another approved biological feature;
- stable temperament: quiet, curious, or gently clumsy, expressed without changing pose.

Do not use waving, walking, leaning, jumping, sleeping, or other action differences to create the illusion of three concepts. If removing the pose would make the candidates indistinguishable, the board has failed.

In `source-faithful`, the subject is the body; do not put it in an animal costume or replace it with a monster. In `flavor-monster`, the creature is the body; do not retain a complete cup, bowl, bottle, wrapper, lid, rim, straw, or container-wall silhouette. In both modes avoid detailed clothing, uniform heavy outlines, smooth digital gradients, solid textureless fills, polished vector outlines, sticker borders, kawaii rendering, glossy 3D shading, realistic faces, text, watermarks, or official brand marks. Cuteness should come from awkward proportion, material marks, and a readable action rather than large eyes.

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

Before drawing actions, record a compact canonical lock from the master: selected character mode, face coordinates, appendage inventory and lengths, outer silhouette proportions, defining object geometry or monster anatomy, color/material zones, foot anchor, and the characteristic amplitude of line waviness. Pose references may change gesture but never override this lock.

For `source-faithful`, keep the public schema-v2 action set:

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

Interpret these v2 states through source identity:

- Object physics and source-specific verbs lead. Preserve the source silhouette and structure through every action; use bubbles, wobble, crumbs, roll, steam, melt, light, or another real property for `signature` and `play`.

Optional runtime-extension actions stay compatible with schema v2:

| State | Visual purpose | Runtime trigger | Art expectation |
|---|---|---|---|
| `fall` | Bridges a high drag release into `land` | Release above the floor | 3–5 looping frames; held/tucked pose → airborne pose → landing anticipation; no floor line |
| `touch` | Gently acknowledges a nearby cursor | End of one bounded cursor chase | 4–6 frames; neutral → reach toward one side → retract → neutral; mirrorable |

For `flavor-monster`, define 6–10 schema-v3 behaviors; do not pad the set to twelve. Every required binding must resolve to one behavior, and every behavior must be reachable from a binding. The current eight-behavior reference is:

| Behavior | Phases | Purpose |
|---|---|---|
| `awake-story` | one complete awake episode | Neutral life with one readable internal beat |
| `explore-walk` | `start → walk-loop → stop` | One bounded autonomous exploration |
| `sleep-cycle` | `sleep-enter → sleeping-loop → wake-exit` | Persistent sleep without snapping to neutral |
| `affection-click` | one complete response | Acknowledges one click |
| `cursor-encounter` | `notice → approach → touch → retreat → settle` | One bounded cursor meeting and return |
| `held` | `grab-enter → held-loop` | Continues until pointer release |
| `drop-recover` | `fall-loop → impact → rebound → settle` | Connects gravity impact to recovery |
| `fruit-hiccup` | one complete flavor event | Expresses source DNA with larger amplitude |

Use per-phase PNG/WebP strips. A phase declares either fixed `fps` or one `durationsMs` value per frame, never both. `once` phases normally finish on animation; loops must have an explicit external exit such as motion completion, floor impact, pointer release, wake request, or timeout. Mark grounded phases with `grounding: "floor"` so the runner aligns each frame's visible bottom to the fixed foot anchor; use `grounding: "free"` for held or airborne phases. Reuse approved frames by splitting and ping-ponging where the boundary is clean; do not redraw approved motion merely to satisfy a file layout.

Choose the physical floor separately from the drawing baseline. Keep the default `work-area` when a pet must avoid the Dock/taskbar. Use manifest `floorMode: "display-edge"` when the approved composition explicitly sits on the screen frame and the reserved system strip would make it look suspended.

When replacing earlier actions, the newest explicitly approved action family is the style baseline. Match its line weight, waviness, media zoning, opacity, face system, and limb construction; do not average old and new styles together. For transition-linked groups (`drag → fall → land`, `walk → touch → walk`), review adjacent end frames side by side and make each boundary share a compatible silhouette.

Use handcrafted/model-generated frames for silhouette-changing poses. Let the runtime supply mirroring, translation, subtle breathing, light sway, heart/Zzz particles, and squash/stretch.

## Stage 4: Motion approval

Provide both for either mode:

- a labeled contact sheet showing every action or behavior at one consistent scale;
- a phase timeline with enter/loop/exit boundaries for schema v3;
- a looping preview that plays the full set without hiding identity drift;
- a dark-background frame audit of every phase.

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
Create a coherent desktop-pet animation strip for the approved character.
Preserve exactly the same silhouette, one-to-three-color palette, minimal crooked face,
appendage inventory, structurally crooked hand-redrawn geometry, hesitant mixed-weight pen,
and source-appropriate hand color. For drinks and soft foods preserve the approved media
zoning: light colored pencil, broad childlike wax crayon, paper-white clear areas, and
only optional pale smears in every frame.
[source-faithful: the photographed subject remains the body and keeps its object structure.]
[flavor-monster: the approved creature remains the body and keeps its biological anatomy;
do not reintroduce a complete source container silhouette.]
Transparent background, no white rectangle, no text, no logo, no watermark, no costume,
no new accessories, no polished vector line.

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
- stable idle never continuously redraws or moves the window; v3 characters may declare a longer 24–36-second idle interval in `cadence`;
- v3 ambient checks and cooldowns are character data, with the current monster using a 15–25-second check, 60-second hiccup cooldown, and 140-second walk cooldown at the balanced baseline;
- cursor proximity may trigger one bounded interaction episode: move toward the cursor by at most 80 px, play `touch`, then return to the exact pre-trigger x position. Lock the target at trigger time; never continuously follow, capture input, or request accessibility permissions.
- releasing a dragged pet above the floor plays `fall` while the window descends monotonically, then `land`; never snap directly to the ground.
- for v3, a press becomes `held` only after the pointer crosses the manifest drag threshold; a stationary release is click-only, and pointer proximity does not reset the sleep clock unless the manifest opts in.
