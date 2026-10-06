---
name: build-upload
description: >
  Build a policy artifact through the mixin's tooling and upload it as a new
  inert version, logging the one change it carries before anything else
  happens. Use at loop step 7, after every attributable change, and for a
  first policy's first upload.
loop_step: 7
---

# Build-upload — routine, inert, and always logged

Uploading enters no competition. It registers a private version, costs
nothing but an eval round if broken, and is the loop's cheapest step by
design — the human's recorded speed stance (see `user_preferences.md`) says
whether any static check runs first; the seed leans fast: **the next eval is
the test**. The one mandatory cost, every time, is the version log row.

## Method

1. **Resolve the live manifest runtime first.** For `game-hosted` file policies, package the game-defined file or directory and use `coworld upload-policy --file <path> --name <policy>`. Verify current CLI help. Do not pass image-only run, secret, or model flags. Then continue at step 3. For `platform-hosted` policies, follow the image build path below.

   **Build through the mixin's tooling** (`games/<g>/tools/`, per MIXIN.md).
   The mixin pins the game/SDK refs the league actually runs — build against
   the pins, never a moving tip (the pin's rationale is recorded next to it).
   Build for `--platform linux/amd64`; arm64 is rejected at upload.
2. **Upload:**
   ```
   coworld upload-policy <image> --name <policy> [--run <argv>] \
       [--secret-env KEY=…] [--use-bedrock [--bedrock-model …]] \
       [--tag purpose=<one-line-change-slug>]
   ```
   - `--run` is required for images containing multiple roles, and its
     absence is **the quietest failure on the platform**: the wrong thing
     runs and every episode times out at worst-case score. When in doubt,
     set it; then verify the new version's run attribute before its first
     eval (`eval_request.py resolve` shows the version registered; the
     version's attributes are checkable via the stats API).
   - Secrets ride `--secret-env`, never image layers.
3. **Write the version log row — before anything else.** In
   `games/<g>/players/<policy>/VERSION_LOG.md`: version, policy-version id
   (from the upload output), UTC timestamp, **the one change and its
   mechanism**, runtime config, validation state `unvalidated`, honest notes.
   An upload without its row is a hole in the campaign's memory
   (non-negotiable #2). This skill is not done until the row exists.
4. **Hand to `run-eval`** — a crash-test rung if the change touched
   plumbing, straight to the question's eval otherwise.

## Footguns

- **Docker layer-cache staleness:** a build arg that names a branch (not a
  resolved commit) can silently reuse a cached layer when the branch moves —
  the mixin's build tooling should resolve refs to commits before the build;
  if it doesn't, do it yourself and note it as a mixin gap.
- **Two changes in one version** tells you nothing about either — if you
  notice a second change sneaking in, split the upload.
- **"Latest" is not a version.** Records and rosters always name `name:vN`.

## Handoffs

- **Consumes**: the mixin's build tooling and pinned refs; the change from
  loop step 6.
- **Produces**: an inert version + its log row.
- **Hands to**: `run-eval` (the upload's first test), eventually
  `ab-compare` (validation state updates), `submit` (never directly — only
  the human gates that).
