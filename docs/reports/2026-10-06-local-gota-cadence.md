# Local GOTA cadence iteration — 2026-10-06

## Conclusion

The candidate is a functioning local BASIC policy, but the proposed benefit is unproven. Both one-match arms reached `time_limit` at 28,909 ticks and scored zero in all ten seats. Every player VM started and completed with exit code 0 and no BASIC errors. The changed policy therefore passed local integration; these one-seed outcomes do not establish a strength gain or champion claim.

## Objective and source provenance

This was one bounded local iteration only: baseline match followed by candidate match, no more than two matches. No hosted practice, policy upload, league/credit change, or credential read occurred. The local player was `ply_762bc195-556b-4f65-aed3-c17cc4afe660`.

The supplied fixture README identifies the official source as `https://github.com/Metta-AI/polyworld` at `150119c89b3535eb353af75c5bf5bc22b36e31f2`; README SHA-256 is `d14b79d4219dc949d453eaa7c44d792e12db140f73301f7fc0068e0d7594c394`. This is the corrected source provenance supplied for this run. Fixture hashes: `base.bas` `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`; executable `gota` `7cae465c33acc583caaf294001efcfc159f4d4367cbd2eb61e31d4f92b216023`; `manifest.json` `e26a69b7fb3c4a731347996ce51c0be5622e10d8e2aaa87355008c2d8392805d`; protocol `coworld.nim` `64a97900fcffdf6c0e0f0c476d309371b873568f59e9cd2d75d6dc76fa096b9a`; `configs.nim` `19cb7a1c31cc39bf3e9c9e25ff64424cc321f27756a4e8f8503ecaca7d86631e`.

## Hypothesis and single change

In `policy.bas`, the main decision cadence changed from `nextThink = match.tick + 6` to `nextThink = match.tick + 3`. Hypothesis: more frequent decisions reduce the time until a policy responds to newly sampled observations (such as target changes or visible warnings), at the cost of more VM invocations. The baseline and candidate source differ only in this cadence value. Baseline SHA-256: `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`; candidate SHA-256: `6e7b98669816511cdd0c1b27bf93e3c9471dc39266c5df8bfb120b308a3532da`.

The hypothesis was recorded before the matches, but no formal score threshold was specified and this pair does not isolate response latency. The benefit is therefore inconclusive, not confirmed.

## Exact local configuration

Both configurations used `seed=2026`, `max_ticks=28800`, `spawn_interval_ticks=480`, and `headless_tick_rate=0`. Each had exactly ten seats and the same non-secret placeholder token strings `local-seat-0` through `local-seat-9`. The `players` array used the local player as slot 0 (`ply_762bc195-556b-4f65-aed3-c17cc4afe660 (baseline)` or `(candidate)`) and `Baseline 1` through `Baseline 9` in slots 1–9. Thus the only JSON config difference was slot 0's descriptive label. Baseline ran the original source in all ten slots. Candidate ran the changed source in slot 0 and byte-identical baseline source in slots 1–9. No explicit `map_preset` or `draft_mode` fields were supplied; this is the exact config provided to the fixture, and both arms used the same defaults.

| Arm | config.json SHA-256 | seats.json SHA-256 | Wall time |
|---|---|---|---:|
| Baseline | `9b6d3e77d9a670ea410e2c8163a42e055652a8bb80e7faafb7a2bb4627ccd140` | `60deb43503b52cdc047aa045d8f7fdb5fe62cbfe123135b8b61c9170b3444329` | 10.574 s |
| Candidate | `2465167ca3ff8cc0665b14279dca0cc463f5824e84e524f83d9168f7e60e7d0d` | `94d077257ec5ffe2bac760ffda120826379212cc1546e0af6247195f53d685aa` | 13.040 s |

The file-handoff evaluator is `games/gota/instruments/local_eval.py`, SHA-256 `baaf8f11e9c659f8728271ceb9b7d2d36249c950a694f2f88dd8f07598725ce9`. It stages per-seat files, config and seats JSON with `file://` URIs, waits for the atomic results file, then terminates the game process. Both runs recorded `process_termination=results_published` and process exit code 0 after termination.

## Results by seat

The five slots on Red are 0–4; slots 5–9 are Blue. Match results are `time_limit` at 28,909 total ticks (including draft) in both runs. Scores were zero for every slot in each run. XP below is included as local game telemetry only; it is not a win or strength metric.

| Slot | Team | Baseline score | Candidate score | Baseline XP | Candidate XP | XP change |
|---:|---|---:|---:|---:|---:|---:|
| 0 (local player) | Red | 0 | 0 | 1664 | 2468 | +804 |
| 1 | Red | 0 | 0 | 2290 | 2469 | +179 |
| 2 | Red | 0 | 0 | 1692 | 2408 | +716 |
| 3 | Red | 0 | 0 | 3510 | 3484 | -26 |
| 4 | Red | 0 | 0 | 3236 | 1928 | -1308 |
| 5 | Blue | 0 | 0 | 2410 | 1931 | -479 |
| 6 | Blue | 0 | 0 | 2933 | 3078 | +145 |
| 7 | Blue | 0 | 0 | 1843 | 2416 | +573 |
| 8 | Blue | 0 | 0 | 3401 | 2108 | -1293 |
| 9 | Blue | 0 | 0 | 2430 | 4634 | +2204 |

## Logs and replay metadata

For each arm, all ten private player logs were 49 bytes and contained the slot's start and completion messages. No log contained a `BASIC error:` diagnostic. All ten status records were `exited`, reason `Completed`, exit code 0. The evaluator observed the results file only after publication, then terminated the still-running HTTP/game process as the protocol requires.

Baseline replay: 572,222 bytes; SHA-256 `b8d1c57985ef956ce70a1dbc756a9496649bc9c2ba3a69b5ad0dbfbc8d6601a8`. Candidate replay: 571,263 bytes; SHA-256 `215258c01992d34bcd46a741158394c17b9020327d5c27eb8266913e8d74216a`. Both replay prefixes identify `POLYWORLDREPLAY` and `gods_of_the_arena`; the headers contain the ten configured player labels. This is metadata inspection only, not a full replay event decode.

Raw results, all seat logs, `player-status.json`, configs, seats manifests, stdout and replay files are retained locally under `.runtime/gota-local/{baseline,candidate}/` (ignored by Git). The results JSON, logs and replays were actually read/checked before recording the findings.

## Interpretation and limits

Local functionality is verified for both versions. There were two matches total, one per arm, one seed, and all seats were identical baseline opponents except for candidate slot 0. Both matches timed out and every score was zero. The seat-level XP shifts are descriptive single-game outcomes and cannot show a reliable advantage. Because the replay body was not decoded into action events and no latency metric was collected, the observation-response mechanism remains untested. This is local integration evidence only; no hosted strength or champion claim follows.

## Source commits and publication status

Policy repository: `https://github.com/djbhindi/softmax-policy-762bc195-556b-4f65-aed3-c17cc4afe660`, branch `agent/local-gota-20261006-762bc195`. Baseline seed commit `369de10969855e323709eeedefc6f7ff33523c60`; candidate source commit `066d720bc086bce2a68e2057bcc37cc43a4d10d8`; final policy documentation/results commit `6e0706fe2a3357ca22cd8a16103f0daa5c5b205e`.

The policy push was attempted once using its configured HTTPS remote and failed before authentication: `fatal: could not read Username for 'https://github.com': terminal prompts disabled`. No credential was read or substituted. The local branch and commits remain intact; remote publication is blocked by the Git client having no usable credential in this session.
