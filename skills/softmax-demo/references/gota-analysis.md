# GOTA strategy and replay analysis

Read bundled gota-guide.md for mechanics and the hosted manifest's participation guide for release-specific changes.
Bundled docs were retrieved from Metta-AI/polyworld on 2026-10-06; compare to the actual hosted source revision.
The reference baseline handles drafting, leveling, shopping, farming, healing, pushing and finishing. Start there.
Choose one explainable parameter or decision change after inspecting the field; don't invent a new policy architecture for the smoke.

Two teams of five: slots 0–4 Red, 5–9 Blue. Winning heroes score floor(lifetime XP / elapsed simulated minutes).
Loss/draw/timeout scores are zero. Draft time counts. The live release remains authoritative.
Separate team victory, match duration, hero XP, deaths, structures and role/seat effects. A faster loss is not an improvement.
Do not confuse league rating with a single episode's Glory score.

## Replay interpretation

Downloading bytes is not analysis. Use the hosted replay viewer and report concrete observed events, or decode using matching source.
The supported native path is Polyworld's GOTA replay tools, documented in gota-upstream-tools.md.
Build prerequisites: Git/LFS, C compiler, libcurl, Nim >=2.2.10, Nimby, Polyworld source and polyworld_art assets.
Follow the official runbook's dependency installation and build steps, but NEVER run its 1000-game tournament example.
Compile against the exact game source revision that produced the replay. A mismatched decoder must fail visibly.

Never dump the standalone replay_extractor's default output: it prints every object on every tick.
It can exceed the entire hosted disk. A larger disk does not fix that failure.
Use the upstream `inspect_players REPLAY METADATA OUTPUT_JSON` for compact verified counters;
build with `-d:replayEvents` against the exact source revision. Follow the metadata contract in
upstream herostats.nim; do not invent fields. Quiet replay_extractor verifies hashes only.
Run every compiler and replay tool through this skill's `scripts/bounded_run.py`:

```sh
python3 "$SKILL/scripts/bounded_run.py" --state-dir "$RESEARCH/.runtime/operations" \
  --key baseline-replay --retry-safe --seconds 120 --output-mib 8 --file-mib 64 \
  -- /absolute/inspect_players /absolute/baseline.replay /absolute/metadata.json /absolute/stats.json
```

Use a distinct key per input hash and tool revision. At most two attempts per local operation.
The runner records timeout/output/disk/failure states; never treat partial output as a valid replay.
Keep compilation single-threaded (`--parallelBuild:1`). Inspect selected event intervals, not a full state dump.
On a resource failure, retain original replays, source, credentials and records. Remove only reproducible
build/cache outputs identified by the operation record; do not clear the instance or another workspace.

For at least one decisive interval, explain what the policy did, the observed consequence, and evidence supporting the next change.
If native dependencies cannot run, use Hermes browser tools with the hosted viewer and cite timestamps/ticks actually inspected.
If neither viewer nor decoder works, stop at a replay-analysis failure; do not substitute a guessed narrative from final scores.

## Required game skill bindings

Evaluation: one baseline and one candidate smoke with pinned opponents and normal rules; larger significance claims require a new approved budget.
A/B: match roster/configuration, report every seat and team, exclude infrastructure failures, label two episodes inconclusive for strength.
Survey: prioritize crashes, zero-score timeouts, early deaths, stalled pushes, and large baseline/candidate differences.
Diagnosis: connect an observed failure to one source location and one falsifiable change.
Replay: source-matched verified decoding or actual hosted viewer inspection as above.
