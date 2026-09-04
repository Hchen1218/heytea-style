# Desktop Pet Pack v2 / v3

Read this reference when exporting, validating, importing, or upgrading a desktop-pet pack.

## Schema-v2 directory contract

```text
pet-id/
├── pet.json
├── preview.png
└── animations/
    ├── idle.webp
    ├── walk.webp
    ├── rest.webp
    ├── happy.webp
    ├── drag.webp
    ├── land.webp
    ├── wave.webp
    ├── signature.webp
    ├── curious.webp
    ├── stretch.webp
    ├── tiptoe.webp
    ├── play.webp
    ├── fall.webp        # optional runtime extension
    └── touch.webp       # optional runtime extension
```

PNG is also accepted. Every animation is one horizontal strip with real alpha; each frame matches the declared canvas. `preview.png` is a human-facing review image and is not rendered in the overlay.

## Manifest v2

Keep the v1 field shape, set `schemaVersion` to `2`, declare all twelve actions, and default new characters to `defaultScale: 0.6`. Each action declares `file`, `frames`, `fps`, `loop`, and `mirrorable`. `walk` must be mirrorable. Recommended current-pet values are `idle` 4 frames at 4 FPS and non-looping, and `walk` 6 frames at 6 FPS.

Required actions are `idle`, `walk`, `rest`, `happy`, `drag`, `land`, `wave`, `signature`, `curious`, `stretch`, `tiptoe`, and `play`.

Recognized optional actions are `fall` and `touch`. A v2 pack remains valid without them; the runner falls back to `drag → land` and `wave`. Unknown action names remain invalid. If present, `fall` should loop and `touch` should be mirrorable.

## Manifest v3

Schema v3 is the public format for `flavor-monster`. It keeps the common identity, canvas, anchor, hitbox, palette, and scale fields, replaces `actions` with 6–10 freely named `behaviors`, and adds trigger `bindings`. Required bindings are `idle`, `ambient`, `sleep`, `click`, `pointer`, `drag`, and `release`.

Packs using the current v3 grounding and physical-floor contract require runner 3.1.0 or newer.

The optional common field `floorMode` chooses the physical bottom plane: `work-area` stays above the macOS Dock or Windows taskbar and remains the backward-compatible default; `display-edge` uses the true display edge for pets that should not appear suspended above an unused reserved strip.

Each behavior contains one or more ordered phases. Every phase owns a PNG/WebP horizontal strip and declares:

- a unique phase `id`, safe relative `file`, and `frames`;
- exactly one timing form: `fps` or per-frame `durationsMs`;
- `playback` as `once` or `loop`;
- `completeOn` as `animation-finished`, `motion-finished`, `floor-impact`, `pointer-released`, `wake-requested`, or `timeout`;
- optional `motion` as `walk`, `fall`, `cursor-approach`, or `cursor-return`;
- a boolean `mirrorable`.
- optional `grounding` as `floor` or `free`; floor phases align each visible frame's transparent-pixel bottom to `anchor.y`, while free phases preserve airborne or held poses.

An optional v3 `cadence` object may define `idleIntervalMs`, `ambientIntervalMs`, `postEpisodeQuietMs`, `pointerDwellMs`, `pointerCooldownMs`, `dragThresholdPx`, `pointerResetsSleep`, and `profileMultipliers` (`quiet`, `balanced`, `lively`). Cadence is character data: the runner applies the profile multiplier only to autonomous timing and cooldowns; click, drag, sleep duration, and animation timing remain unscaled.

A loop may not complete on `animation-finished`; it needs an explicit external exit. All behaviors must be reachable through bindings. Sleep declares inactivity delay and an automatic wake range, and its behavior must include a persistent wake-requested phase.

## Invariants

- `schemaVersion` is `2` or `3`; ids use lowercase ASCII letters, digits, and hyphens.
- Canvas is 32–1024 px; anchor and hitbox stay inside it; palette has one to three `#RRGGBB` colors.
- Every action or phase path is safe and relative, uses PNG or WebP, and has 1–24 frames. v2 uses 1–30 FPS; v3 may instead use per-frame durations.
- Strip width is `canvas.width × frames`; height is `canvas.height`; every frame is non-empty and corners are transparent.
- In schema v2, stable `idle` and `walk` body-center drift is at most 1 px and their grounded baseline drift is at most 1 px. In schema v3, use phase-level `grounding: "floor"` for variable-height poses; the runner normalizes each visible frame to the shared anchor.
- `floorMode: "display-edge"` is appropriate only when the approved pet should sit on the actual screen frame; omit it to preserve Dock/taskbar avoidance.
- `idle` visible-height variation is at most 1.5%; loop seams must not make a large silhouette jump.
- At `defaultScale`, visible height should land near 120–140 px.
- ZIP has one top-level directory named after the id and contains no traversal, symlink, encryption, or oversized members.

## Review and build

Before motion approval, create artifacts only:

```bash
python3 scripts/desktop_pet.py review path/to/pet-id
```

For v2, the required-only contact sheet is 3×4. For v3, the overview contains one cell per behavior and `behavior-timelines.png` shows phase boundaries and completion events. Both formats also produce `motion-preview.gif` and `frame-audit.png`, which places every frame on a contrasting dark background. After explicit approval, build, independently validate, and write the delivery folder in one step:

```bash
python3 scripts/desktop_pet.py pack path/to/pet-id
```

Defaults write the ZIP, review artifacts, and start/quit entrypoints under `generated-pets/`. Pass `--out`, `--review-dir`, and `--delivery-dir` to override. The older `build_desktop_pet_pack.py` / `validate_desktop_pet_pack.py` commands remain valid. Validation errors name the file and frame and include a one-line fix hint; `--json` is available on `validate_desktop_pet_pack.py`.

For a non-technical-user delivery, `pack` already writes the platform folder. To target another OS:

```bash
python3 scripts/desktop_pet.py pack path/to/pet-id --delivery-platform windows
```

The delivery folder contains the ZIP, `preview.png`, `使用说明.txt`, and two lightweight entrypoints: `启动桌宠` passes `--open-pet` to the installed shared runner; `关闭桌宠` passes `--quit`. macOS uses executable `.command` files and Windows uses `.cmd` files. Do not place the Electron application, dependencies, imported runtime data, or a second copy of the runner in this folder.

## v1 upgrade boundary

The runner must never run, delete, or overwrite a schema-v1 pack. It lists v1 packs as needing upgrade and offers their folder. The Skill copies the original eight actions into a new draft, reloads the canonical identity, stabilizes old frames, generates the four new actions, asks for motion approval, and only then builds a new v2 ZIP. The v1 ZIP remains recoverable.

## Runner contract

The Electron source template imports validated v2 and v3 ZIPs and compiles both into one internal episode model. It keeps one active pet, uses alpha click-through, constrains movement to display work areas, and persists scale, activity level, cursor awareness, position, pause, visibility, topmost, and launch-at-login. Interactions preempt autonomous episodes; reduced-motion selects quiet behavior and disables autonomous exploration and cursor chase while preserving required drag-release recovery. v3 sleep remains in its loop until a wake request, and physical completion events advance walk, cursor, and fall phases. Right-clicking an opaque pet pixel opens the native pause/activity/size/switch/hide/quit menu; the tray remains the fallback when the pet is hidden.

For v3, a pointer press is pending until it moves past `dragThresholdPx`: release before the threshold is one click, while movement past it is one drag/release chain. Pointer proximity does not count as sleep-resetting interaction when `pointerResetsSleep` is false.

Do not copy `node_modules`, build output, imported packs, or user app data into the skill.
