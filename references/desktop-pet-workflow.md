# Desktop Pet Workflow

Read the identity stages of this reference for static character requests. Read the environment, motion, approval, and packaging stages only when the user chooses a runnable desktop pet.

## Outcome

Turn one photographed subject into an approved canonical character and, only when requested, a quiet runnable desktop companion recognizable at small size and importable into the bundled runner.

This mode is a full illustration conversion. Unlike poster mode, it does not preserve photographic texture.

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

## Stage 2: Character-mode and identity-brief gate

Read `desktop-pet-character-modes.md`. If the user has not already chosen a mode, ask whether they want:

1. `source-faithful`（写实卡通桌宠）—the photographed subject remains the character body; or
2. `flavor-monster`（风味小怪兽桌宠）—the photograph supplies flavor DNA for a newly designed creature.

Stop before candidate generation until the mode is explicit. Do not recommend, default, or infer one from the subject category. When the request already says 写实卡通、保留原物形态、小怪兽, or otherwise makes the choice unambiguous, record it and continue without asking again.

Extend the identity brief according to the selected mode:

- `source-faithful`: record outer silhouette, major internal divisions, and must-preserve object/container details.
- `flavor-monster`: select no more than three identifying visual signals, require at least two kinds of identity DNA chosen from color, ingredient, and material, and map them into a source-derived body topology, crayon field, crude flat marks, restrained irregularities, or regional medium. Record the body silhouette and center of gravity; a regional material plan assigning every major zone to long loose lightly layered colored-pencil sweeps, a few broad open wax-crayon arcs or separated blocks, significant irregular internal paper-white, or an occasional faded edge; exactly two arms and two legs with black-line attachment points, lengths, proportions, and resting pose; facial-mark count, placement, black-line shape, and friendly emotion; the planned full-length meander plus within-stroke pressure or thickness variation of every face and limb mark; a cuteness check with explicit grotesque-organic exclusions; one stable floor anchor; and source-specific motion verbs reserved for later behavior design. Also record every literal source structure that must be discarded. Do not lock the source silhouette or save the full generation prompt unless the user explicitly requests a prompt file.

## Stage 3: Identity design

Before prompt writing, inspect the five boards listed in `mixed-media-style-guide.md` and distinguish positive controls from the failure reference.

For a `flavor-monster` identity generation, provide exactly these model-facing roles:

1. the uploaded photo supplies visual identity DNA from color, ingredient, and material, plus a separately recorded motion verb for later behavior design;
2. `examples/desktop-pet/pink-green-flavor-monster-v3/preview.png` controls HEYTEA-like cuteness, handmade awkwardness, and the relationship between a mostly unoutlined color body and sparse black doodle face/limbs; explicitly forbid copying its body topology, protrusion placement, face layout, or proportions;
3. `contact_sheet_dry_media_wavy_line_v4.png` controls region-specific colored-pencil scumbling, sparse wax-crayon marks, significant internal paper-white, paper tooth, and continuously wandering strokes; it must not become a uniform texture layer over the whole body;
4. `contact_sheet_thin_stroke_anatomy_v2.png` controls full-length meander, within-stroke pressure and thickness changes, black dry breaks, open joins, overshoots, and retracing in exactly two arms, two legs, and every facial mark.

State these roles in the generation instruction and forbid copying people, lettering, objects, layouts, logos, or packaging from the study boards. Use `contact_sheet_figure_actions_v2.png` only after identity approval during motion generation. Use `contact_sheet_smudged_paint_structure_v3.png` only for a focused repair that needs fading edges or paper intrusion. Do not pass `contact_sheet_mixed_media_objects_v2.png` as a positive generation reference; inspect it only after generation when diagnosing over-hatching or object-heavy material treatment.

### Two-pass construction or repair

For `source-faithful` mixed-media drinks and soft foods, retain the existing two-pass construction. For `flavor-monster`, default to one complete-color generation in which the crayon body mass and sparse line marks are resolved together. Enter this two-pass repair only when the first result has flattened media, mechanical geometry, or coloring that completes, smooths, or replaces the intended sparse line system:

1. **Line skeleton**: generate the three `source-faithful` candidates, or the one `flavor-monster` repair target, in black on warm white with no color or shading. Borrow only line behavior from poster-mode `figures/full-poses/*` and `lettering/strokes/*`. Every stroke must visibly meander with shallow waves, drifting curvature, and pressure wobble. Use gaps, overshoots, retracing, and bad joins as secondary traits. For `source-faithful`, require structural asymmetry in the source rim, opening, walls, lid, base, and perspective when present. For `flavor-monster`, the repair skeleton contains the approved black-line face, exactly two open black-line arms, exactly two open black-line legs, and only necessary partial body guides; it must not add a complete enclosing body contour or conventional mascot anatomy. Reject ruler-straight or colored limbs and facial marks even when they are broken into fragments.
2. **Locked color pass**: use the accepted skeleton as the edit target. Preserve every black stroke, gap, face, limb, and position exactly. Add color behind the line only. Use the dry-media/wavy-line board to assign colored pencil, childlike wax crayon, graphite, active paper-white, and optional pale wash to different material regions. For `flavor-monster`, require visible irregular paper gaps inside the body, allow selected misses, faded ends, or slight boundary crossings, and let light regions remain mostly paper-white with faint traces. Do not redraw, complete, smooth, or repair the line while coloring; do not apply one equal-density texture across the full body; and do not substitute uniform noise, dense tiny strokes or loops, or crosshatching for hand-applied media.

Keep both repair artifacts. The colored result is not allowed to bypass a failed line skeleton.

For `source-faithful`, generate one review board with three full-body candidates on white or warm white. All three must use the same source at the same scale, in the same neutral front-facing stance, with arms relaxed and feet on one shared ground anchor. A candidate board compares identity design, not animation poses.

For `flavor-monster`, generate exactly one best complete-color identity on white or warm white unless the user explicitly asks for multiple directions. Use a quiet identity-readable resting pose, generous negative space, and one shared ground anchor. The first impression must be a cute, friendly, independent flat doodle creature; source recognition comes second through the identity brief. The public example supplies style and cuteness only, while the photo-derived brief supplies the new body topology.

Keep constant in both modes:

- source palette;
- thin-to-medium hesitant black line structure whose important strokes meander along their full length and vary pressure or thickness within the same mark, with occasional dry breaks, retracing, open joins, and overshoot; for `flavor-monster`, apply this primarily to the face, two arms, two legs, and sparse partial marks rather than a complete body contour;
- structurally crooked geometry rather than a clean template with a wobble filter;
- source-appropriate material zoning; for drinks and soft foods, combine long loose lightly layered colored-pencil sweeps, a small number of broad open wax-crayon arcs or separated blocks, paper-white clear areas, and only optional pale smears rather than one uniform treatment. For `flavor-monster`, the paper-white must form significant irregular gaps inside the body; paper grain showing through a fully packed fill does not satisfy this requirement.

For `source-faithful`, also keep the source outer silhouette, major internal divisions, and recognizable container, topping, label-free package, or ingredient details. Vary only:

- placement and size of the minimal crooked face;
- short arm and leg proportions;
- structural crookedness and stable temperament: quiet, curious, or gently clumsy, expressed without changing pose.

For `flavor-monster`, lock:

- one soft, compact, friendly, source-derived dry-media color-mass body with no complete black enclosing outline and no literal source-object silhouette;
- one declared region-by-region material plan with visible internal paper-white, differentiated pencil/crayon density, and selected incomplete or faded edges;
- exactly two separate open black-line arms and two separate open black-line legs, including attachment points, lengths, proportions, and resting pose;
- a sparse, friendly black-line face whose structure may vary through one or two eyes, offset placement, or no conventional mouth;
- at least two kinds of visual identity DNA chosen from color, ingredient, and material and transformed into the body topology, color field, crude flat marks, paper gaps, restrained irregularities, or regional medium—not literal ingredient anatomy;
- one separately recorded motion verb reserved for later behavior design and motion approval;
- a stable quiet, curious, or gently clumsy temperament expressed without an action pose;
- a cuteness pass that rejects fleshy collapse, realistic tissue, slime, horror tendrils, corpse-like sagging, sharp grotesque anatomy, or any disturbing organic reading;
- a discard list covering every literal source structure and brand-like mark that must not survive.

Do not use waving, walking, leaning, jumping, sleeping, or other action differences to create the illusion of three concepts. If removing the pose would make the candidates indistinguishable, the board has failed.

In `source-faithful`, the subject is the body; do not put it in an animal costume or replace it with a monster. In `flavor-monster`, the creature is the body; do not retain a complete cup, bowl, bottle, wrapper, pizza slice, mushroom, ingredient, or other literal source silhouette. In both modes avoid detailed clothing, uniform heavy outlines, smooth digital gradients, solid textureless fills, polished vector outlines, sticker borders, kawaii rendering, glossy 3D shading, realistic faces, text, watermarks, or official brand marks. For `flavor-monster`, also reject colored, volumetric, missing, or tendril-replaced limbs and any fleshy, slimy, corpse-like, sharp, or horrific body reading. Cuteness should come from soft compact proportions, material marks, sparse black doodle features, and friendly temperament rather than large eyes.

For `source-faithful`, ask the user to choose candidate 1, 2, or 3, or request a focused revision. For `flavor-monster`, ask the user to approve the single concept or request a focused revision of it. Repair only the failed axis: revise the body when it is literal, unpleasant, or insufficiently cute; when it is fully packed or every region shares one texture, preserve topology, DNA, face, limbs, and anchor, add the smudged-structure board for that repair only, and rebuild only the regional media and internal paper-white; when the face or limbs are smooth or constant-width, preserve the body and color regions and redraw only those marks at their existing locations with full-length meander and within-stroke variation; and repair only the inventory when an arm or leg is missing. Do not infer approval from silence, and do not turn a rejected monster concept into a three-candidate board unless the user requests broader exploration.

Before presenting the identity, perform an appendage inventory. `source-faithful` candidates default to exactly two arms and two clearly visible legs. Every `flavor-monster` must have exactly two separate open black-line arms and two separate open black-line legs. Broken-line style may create gaps, but it must not change the 2+2 count, merge a limb into the body, replace a limb with a tendril or colored stroke, or turn it into a volumetric paw, mitten, foot, toe cluster, or realistic joint.

### Identity-scale gate

Inspect the generated identity at full resolution, then render or view it at 120–140 px before requesting approval. Reject or focus-revise it when:

- a complete cup, bottle, bowl, wrapper, rim, lid, straw, container wall, layered-liquid cross-section, logo-like mark, text, prop, or background scene survives;
- the small version no longer reads as one soft, compact, friendly source-derived color body with a sparse black-line face, two black-line arms, and two black-line legs;
- fewer than two kinds of visual identity DNA chosen from color, ingredient, and material remain recognizable after reduction;
- the friendly black-line face or quiet resting posture becomes unreadable;
- the feet or approved body-bottom substitute do not share one stable ground anchor.
- significant irregular paper-white is absent from inside the body, reads only as fine paper grain under saturated color, or disappears into compression noise after reduction;
- major color regions collapse into undifferentiated speckle, or every region uses the same density and mark type;
- a face or limb stroke is a smooth Bézier-like curve, constant-width monoline, or clean vector path with superficial jitter, or its pressure variation makes a required feature disappear at small size;
- a complete enclosing black body outline, colored or volumetric limb, missing arm or leg, tendril substitution, realistic or shaded facial feature, large chibi eye, literal ingredient organ, fleshy collapse, slime, horror anatomy, corpse-like sagging, or shaded mascot volume becomes the dominant reading.

White or warm-white paper is review-only. Approval locks the identity but does not authorize a paper background in runtime assets, which must use real alpha transparency.

### Pose-only consolidation

If a `source-faithful` board, or a user-requested multi-direction monster board, already has one shared identity and differs only through pose:

1. State that these are motion sketches, not valid identity variants; do not force a meaningless three-way choice.
2. Use the most neutral standing pose to create one canonical master with fixed source geometry or monster graphic grammar, face placement, appendage count and proportions, line behavior, media zoning, and ground anchor.
3. Treat the other poses only as motion references. A raised arm may inform `wave`; a tilt may inform `happy` or `land`.
4. Obtain explicit approval of the consolidated identity before motion generation. Keep the canonical master as the sole identity reference for every action.

## Stage 4: Identity approval and continuation gate

Do not infer approval from silence or from a request that originally mentioned a desktop pet. Explicit identity approval locks one canonical master; it does not authorize motion generation, environment installation, or poster generation.

For an approved `flavor-monster`, ask the user to choose:

1. 制作融合海报；
2. 继续制作可运行桌宠；
3. 两者都做。

If the user chooses a fusion poster, route that branch to `monster-poster-workflow.md` and ask for 带字版、无字版或两套都做 unless already specified. The poster branch does not use the runner environment gate.

If the user chooses a runnable pet, or explicitly requested a `source-faithful` runnable pet and has now approved its canonical identity, continue to Stage 5. If both branches were selected, they proceed independently: a blocked runtime branch must not block the static fusion poster.

## Stage 5: Runnable-branch environment gate

Only after canonical identity approval and explicit selection of a runnable desktop pet, read `desktop-pet-environment.md` and run the read-only preflight:

```bash
python3 scripts/check_desktop_pet_environment.py --json --required-schema 3
```

If anything is missing, show one concrete repair plan and ask for installation or upgrade consent immediately before making that change. After approval, fill only the missing components, rerun preflight, and stop the motion branch if it still does not report `ready`. If the user declines, keep the approved static identity and any fusion-poster branch available without promising runnable output.

This system gate is separate from both human visual approval gates. It must pass before motion generation, but it must never run merely to create a static monster or fusion poster.

## Stage 6: Motion design

After character approval, make a consistent action model sheet. Use the approved candidate as the only identity reference.

For `flavor-monster`, this is the first stage where `contact_sheet_figure_actions_v2.png` may be passed as a positive reference. It controls gesture economy and primitive limb movement only; the approved canonical master remains the sole identity source and the action board must not redesign the color mass, face, marks, or appendage inventory.

Before drawing actions, record a compact canonical lock from the master: selected character mode, black-line facial marks and coordinates, exactly two black-line arms and two black-line legs with their attachment points and lengths, outer silhouette or color-mass proportions, defining object geometry or monster graphic features, color/material zones, foot anchor, and the characteristic amplitude of line waviness. Pose references may change gesture but never override this lock.

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

## Stage 7: Motion approval

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

## Stage 8: Package and validate

After motion approval, export transparent animation strips, build the pack and platform delivery folder with `scripts/build_desktop_pet_pack.py --delivery-dir ...`, and validate the ZIP with `scripts/validate_desktop_pet_pack.py`.

Return the review artifacts, validated ZIP, manifest summary, and delivery folder. For v3, keep cadence, gesture, per-phase grounding (`floor` or `free`), and any explicit display-edge floor policy in the manifest. The shared Electron runner is installed once; each pet delivery contains only its pack, preview, start/quit entrypoints, and short usage note.

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
[flavor-monster: the approved creature remains the body and keeps its source-derived unoutlined
dry-media color mass, sparse friendly black-line face, exactly two open black-line arms,
exactly two open black-line legs, and abstract flavor marks;
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
