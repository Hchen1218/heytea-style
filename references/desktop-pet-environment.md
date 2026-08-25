# Desktop Pet Environment and Installation

Read this reference at the beginning of every desktop-pet request, before inspecting or generating the user's photo.

## Required entry gate

Run the read-only preflight first:

```bash
python scripts/check_desktop_pet_environment.py --json
```

Interpret the result:

- `ready`: the runner is already installed. Continue to the subject gate without discussing Node or build tools.
- `installable`: the runner is missing, but the bundled source and local Node/npm toolchain can build it.
- `needs-toolchain`: the runner is missing and Node.js 20+ or npm must be installed first.
- `missing-source`: the skill package does not contain the runner source. Stop and report that the runtime cannot be installed from this package.
- `unsupported`: stop. v1 supports only macOS and Windows.

Do not begin image generation until the preflight is resolved. A user may decline installation and still request static concept art, but do not promise a runnable desktop pet or proceed to animation packaging in that case.

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

The script uses no shell interpolation and refuses to replace an existing application. It installs to a per-user location by default:

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
- replace an existing runtime;
- claim that an unsigned local build is a notarized production release.

## After installation

Run the preflight again. Continue only when it reports `ready`. If installation succeeds but the current process cannot yet find a newly installed Node/npm, ask the user to reopen the terminal or Codex task, then rerun preflight. Do not repeat package-manager installation indefinitely.

Once the role pack is built, import it through the runner. Installation is a one-time system step; future pets receive a lightweight delivery folder with the validated ZIP plus start/quit entrypoints. Never copy Electron, `node_modules`, or another full application into each role folder.

The start entrypoint invokes the installed runner with `--open-pet <zip>`; the single running instance validates, imports or refreshes that pack, activates it, and shows the pet. Commands that arrive while the runner is still initializing are queued and executed after its window, settings, and import directories are ready. The quit entrypoint invokes `--quit`, allowing settings and position to be saved before exit. If the shared runner is absent, the launcher reports that installation is required; it must not install software silently.
