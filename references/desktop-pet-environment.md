# Desktop Pet Environment and Installation

Read this reference only after the user has explicitly approved a canonical identity and chosen to continue into runnable desktop-pet motion. Static monster identities and fusion posters do not require this environment.

## Required motion-branch gate

Before generating any motion assets, run the read-only preflight:

```bash
python scripts/check_desktop_pet_environment.py --json --required-schema 3
```

Interpret the result:

- `ready`: the installed runner meets the requested schema's minimum version.
- `upgradeable`: a runner exists but is too old for the requested schema; show the exact in-place or side-by-side plan and request upgrade consent.
- `installable`: the runner is missing, but the bundled source and local Node/npm toolchain can build it.
- `needs-toolchain`: the runner is missing and Node.js 20+ or npm must be installed first.
- `missing-source`: the skill package does not contain the runner source. Stop and report that the runtime cannot be installed from this package.
- `unsupported`: stop. v1 supports only macOS and Windows.

Do not begin motion generation until the preflight is resolved. Identity generation and approved-monster fusion posters may proceed without the runner. If the user selected both poster and runnable-pet outputs, a missing runner blocks only the motion and packaging branch. A user may decline installation and keep the approved static identity or continue the fusion poster, but do not promise a runnable desktop pet in that case.

## Consent boundary

The preflight is read-only and does not need confirmation. Installation changes the user's computer and always requires a concise confirmation immediately before execution.

Tell the user:

- what is missing;
- what will be installed;
- where the application will be placed;
- whether Node.js will also be installed;
- that macOS/Windows may display a security or permission prompt;
- that launch-at-login remains off unless the user separately enables it.

Never treat “make me a desktop pet” as permission to install software. Never silently run a package manager, accept a system prompt, change security settings, or enable launch-at-login.

## Automatic repair after approval

First inspect the exact plan:

```bash
python scripts/install_desktop_pet_runtime.py --json-plan
```

After the user explicitly approves:

```bash
python scripts/install_desktop_pet_runtime.py --yes
```

When Node.js/npm are also missing and the preflight reports Homebrew or winget:

```bash
python scripts/install_desktop_pet_runtime.py --yes --install-toolchain
```

For an installed legacy runner that preflight marks `upgradeable`, explicit consent authorizes:

```bash
python scripts/install_desktop_pet_runtime.py --yes --upgrade
```

The JSON report identifies the installed runner as `runtimeScope: "user"` or `"system"`. The install plan exposes the matching `installMode`: `in-place-upgrade` for a per-user legacy runner and `user-side-by-side` for a system-wide legacy runner.

For `in-place-upgrade`, the upgrader first asks the running app to quit, preserves it as a versioned backup beside the application, copies the new build atomically with rollback on copy failure, and leaves imported pets/settings in Application Support untouched. For `user-side-by-side`, it asks the system-wide runner to quit, leaves that installation unchanged, and installs the new runner in the per-user location without requesting administrator privileges or claiming to create a system-level backup.

The script uses no shell interpolation. It refuses to replace a per-user installed application unless both `--yes` and `--upgrade` are supplied, never overwrites an existing backup (repeated refreshes receive a numbered backup), and installs new or side-by-side builds to:

- macOS: `~/Applications/Doodle Desktop Pet.app`
- Windows: `%LOCALAPPDATA%\Programs\Doodle Desktop Pet\Doodle Desktop Pet.exe`

On macOS it can use Homebrew to install Node.js. On Windows it can use winget to install the Node.js LTS package. If the applicable package manager is absent, stop and give the user the official manual prerequisite rather than downloading or executing an arbitrary installer.

## What gets repaired

The approved installer may perform only the missing steps:

1. install Node.js/npm through the detected trusted package manager when explicitly allowed;
2. run `npm install` inside the bundled runner source when dependencies are absent;
3. build only the current operating-system target;
4. copy the unsigned local MVP into the per-user application directory;
5. launch the runner once for verification.

It does not:

- install Linux support;
- bypass Gatekeeper, SmartScreen, antivirus, or browser security warnings;
- grant accessibility, screen-recording, camera, microphone, or other sensitive permissions;
- enable launch-at-login;
- replace a compatible runtime or silently delete the versioned backup;
- claim that an unsigned local build is a notarized production release.

## After installation

Run the preflight again. Continue only when it reports `ready`. If installation succeeds but the current process cannot yet find a newly installed Node/npm, ask the user to reopen the terminal or Codex task, then rerun preflight. Do not repeat package-manager installation indefinitely.

Once the role pack is built, import it through the runner. Installation is a one-time system step; future pets receive a lightweight delivery folder with the validated ZIP plus start/quit entrypoints. Never copy Electron, `node_modules`, or another full application into each role folder.

The start entrypoint checks the installed runner's full semantic version against the pack schema before invoking `--open-pet <zip>`. Schema v3 currently requires 3.1.0 because phase grounding and display-edge floor policy are runtime features. It must report an actionable upgrade message instead of handing a newer pack to an older runner. A compatible single running instance validates, imports or refreshes that pack, activates it, and shows the pet. Commands that arrive while the runner is still initializing are queued until ready. The quit entrypoint invokes `--quit`, allowing settings and position to be saved before exit. Launchers never install or upgrade software silently.
