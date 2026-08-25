# Desktop Pet Pack v2

Read this reference when exporting, validating, importing, or upgrading a desktop-pet pack.

## Directory contract

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

## Invariants

- `schemaVersion` is exactly `2`; ids use lowercase ASCII letters, digits, and hyphens.
- Canvas is 32–1024 px; anchor and hitbox stay inside it; palette has one to three `#RRGGBB` colors.
- Every action path is safe and relative, uses PNG or WebP, and has 1–24 frames at 1–30 FPS.
- Strip width is `canvas.width × frames`; height is `canvas.height`; every frame is non-empty and corners are transparent.
- Stable `idle` and `walk` body-center drift is at most 1 px; their grounded baseline drift is at most 1 px.
- `idle` visible-height variation is at most 1.5%; loop seams must not make a large silhouette jump.
- At `defaultScale`, visible height should land near 120–140 px.
- ZIP has one top-level directory named after the id and contains no traversal, symlink, encryption, or oversized members.

## Review and build

Before motion approval, create artifacts only:

```bash
python scripts/build_desktop_pet_pack.py path/to/pet-id \
  --review-only --review-dir path/to/review
```

The required-only contact sheet is 3×4; rows expand automatically when optional actions are present. The builder also writes `frame-audit.png`, which places every frame on a contrasting dark background so detached marks and partial white boxes cannot hide in transparency. After explicit approval, build and independently validate:

```bash
python scripts/build_desktop_pet_pack.py path/to/pet-id --out path/to/pet-id-v2.zip --review-dir path/to/review
python scripts/validate_desktop_pet_pack.py path/to/pet-id-v2.zip
```

For a non-technical-user delivery, build the platform folder in the same validated step:

```bash
python scripts/build_desktop_pet_pack.py path/to/pet-id \
  --out path/to/pet-id-v2.zip \
  --review-dir path/to/review \
  --delivery-dir path/to/pet-delivery \
  --delivery-platform macos   # or windows; use all only for cross-platform distribution
```

The delivery folder contains the ZIP, `preview.png`, `使用说明.txt`, and two lightweight entrypoints: `启动桌宠` passes `--open-pet` to the installed shared runner; `关闭桌宠` passes `--quit`. macOS uses executable `.command` files and Windows uses `.cmd` files. Do not place the Electron application, dependencies, imported runtime data, or a second copy of the runner in this folder.

## v1 upgrade boundary

The runner must never run, delete, or overwrite a schema-v1 pack. It lists v1 packs as needing upgrade and offers their folder. The Skill copies the original eight actions into a new draft, reloads the canonical identity, stabilizes old frames, generates the four new actions, asks for motion approval, and only then builds a new v2 ZIP. The v1 ZIP remains recoverable.

## Runner contract

The Electron source template imports validated v2 ZIPs, keeps one active pet, uses alpha click-through, constrains targeted walks to display work areas, and persists scale, activity level, cursor awareness, position, pause, visibility, topmost, and launch-at-login. Stable idle is event-driven; interactions preempt autonomous episodes; reduced-motion selects quiet behavior and disables autonomous walk. With `fall` and `touch`, high releases descend before landing, and cursor awareness runs one short chase-touch-return episode instead of continuous tracking. Right-clicking an opaque pet pixel opens the native pause/activity/size/switch/hide/quit menu; the tray remains the fallback when the pet is hidden.

Do not copy `node_modules`, build output, imported packs, or user app data into the skill.
