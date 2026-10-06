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

The standalone full-tick verifier is examples/gods_of_the_arena/tools/replay_extractor.nim.
Build it with the same installed Polyworld dependency environment:

    nim c -d:release -o:tmp/gota/replay_extractor examples/gods_of_the_arena/tools/replay_extractor.nim
    tmp/gota/replay_extractor /absolute/match.replay --quiet
    tmp/gota/replay_extractor /absolute/match.replay > /absolute/replay-events.txt

The quiet mode verifies hashes/actions but is not behavioral analysis. Inspect event output or use inspect_players
from the official tools build to quantify deaths, hero kills, lane last hits, tower kills and team outcomes.
For at least one decisive interval, explain what the policy did, the observed consequence, and evidence supporting the next change.
If native dependencies cannot run, use Hermes browser tools with the hosted viewer and cite timestamps/ticks actually inspected.
If neither viewer nor decoder works, stop at a replay-analysis failure; do not substitute a guessed narrative from final scores.

## Required game skill bindings

Evaluation: one baseline and one candidate smoke with pinned opponents and normal rules; larger significance claims require a new approved budget.
A/B: match roster/configuration, report every seat and team, exclude infrastructure failures, label two episodes inconclusive for strength.
Survey: prioritize crashes, zero-score timeouts, early deaths, stalled pushes, and large baseline/candidate differences.
Diagnosis: connect an observed failure to one source location and one falsifiable change.
Replay: source-matched verified decoding or actual hosted viewer inspection as above.
