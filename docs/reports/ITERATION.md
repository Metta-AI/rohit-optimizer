# GOTA iteration report — 2026-10-06

## Status

The authorized two-request limit is fully used: both the baseline and one-change candidate each completed one normal ten-seat hosted episode, with no episode errors. Exact requests, episode IDs, immutable uploaded-version UUIDs, outcome and per-seat results are recorded below. Both matches timed out; every official score was zero. Replays were downloaded and hashed, but **neither replay was actually inspected**. The candidate ran successfully in the hosted match (10/10 scripts active in each run), but the experiment is **inconclusive for competitive improvement**; XP movement alone is not a win or performance verdict.

## Authorized scope and safety limits

One bounded iteration: at most two experience requests with one normal ten-seat episode each, existing credits only, no credit grants/refills, no league submission, no background scheduling, and a $10 overall Nous spending cap. Both saved request bodies and idempotency keys were reused as authorized after `coworld xp-request list --mine` reconciliation. No duplicate request, credential changes, or league submission. Coach dailyCredits remained 100 as instructed.

## Live discovery

- Authenticated player: `ply_305f0175-65a2-47ca-9566-69991871b743`.
- GOTA Competition league `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`; Coworld `cow_162aa34f-f447-4c5d-8db3-480ec83e98f4`; live release `2026.10.6.1`.
- Ten BASIC seats, Open Draft, full-game cap 28,800 ticks. Leaderboard MMR and mean game score are distinct metrics.
- Hosted source ref: Polyworld `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`. Reference `base.bas` SHA-256 `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`, matching the baseline.
- Live leaderboard snapshot was taken earlier on 2026-10-06; standings move. Examples: a-aron rank 1, MMR 29.97, mean score 65.42; BeWellBot-Arena:v58 rank 3, MMR 25.61, mean 42.64; existing `arena-crossbow-carry:v33` rank 40, MMR 13.20, mean 1.10. These field figures are context, not evidence from the two episodes.

## Source and immutable upload provenance

- Baseline `hermes-gota-iteration:v1`: source commit `eab20515724dc0ea63ce13551333a155c81f7ce3`; source matches the hosted reference. Immutable uploaded version UUID, confirmed by episode participants: `e1d160b8-a9b9-4a78-8295-e529257cdab8`.
- Candidate `hermes-gota-iteration:v2`: immutable policy commit `856984c58692163e23ee7aa5826a2b180742b3bb`, pushed on `agent/hermes-gota-20261006`. The one source change raises visible enemy-hero target bonus `+60`→`+100` in `readObject`; `policy.bas` SHA-256 `f29640c1c2179795d8154d7ece9b5595b5a76024f49166745af152d3af5f1dee`. Immutable uploaded version UUID, confirmed by episode participants: `a93a31e0-c047-4e3f-8624-f4bdeeef901f`.

## Requests, episodes, and measured results

Both requests pinned the same nine opponent versions in seats 1–9, with our policy in seat 0, seed 2026, Open Draft, `max_ticks=28800`, one episode, private, and LLM spend cap $0. Requests completed successfully; neither was infrastructure-tainted (`error=null`, `error_type=null`, `failed_policy_index=null`). Both manifests show missing `events` and `error_info` artifacts as `not_produced`, not as a request failure.

| Arm | Experience request | Episode request | Hosted job / replay ID | Version UUID | Status |
|---|---|---|---|---|---|
| Baseline v1 | `xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39` | `ereq_19048656-ae8c-4793-8b71-fc17554719e4` | `e8568e8d-c93f-4c22-af15-94721a5ffade` | `e1d160b8-a9b9-4a78-8295-e529257cdab8` | completed, no error |
| Candidate v2 | `xreq_5c2a0c44-f187-4064-9c50-23154038c4c2` | `ereq_385ae031-a7ea-40a9-a384-dd0cb0f453c6` | `35eccc26-828a-43be-a238-ce778e413846` | `a93a31e0-c047-4e3f-8624-f4bdeeef901f` | completed, no error |

| Result | Baseline | Candidate | Difference (candidate−baseline) |
|---|---:|---:|---:|
| Outcome | time_limit | time_limit | same |
| Ticks incl. draft | 28,909 | 28,909 | 0 |
| Official scores, slots 0–9 | 0 each | 0 each | 0 each |
| Our slot 0 total XP | 1,609 | 1,927 | +318 |
| Red team XP (slots 0–4) | 20,939 | 23,113 | +2,174 |
| Blue team XP (slots 5–9) | 15,602 | 13,418 | −2,184 |
| Remaining Red towers / Blue towers | 9 / 5 | 7 / 6 | −2 / +1 |
| Active scripts | 10/10 | 10/10 | same |

Per-seat total XP baseline `[1609,5078,6360,4262,3630,1866,5931,2074,2032,3699]`; candidate `[1927,6882,6254,5647,2403,1719,3938,2218,3902,1641]`. Team and tower outcomes are episode observations; they do not isolate the policy code change. The match timed out with both gods at 400 HP in both episodes. With N=1 per arm and no replay inspection, these differences are directional/descriptive only; there is no evidence the candidate is a winning or improved policy.

## Replay artifacts, links, and inspection boundary

- Baseline replay SHA-256 `bc1938b6ecf37f27ab75488e37753c9dd305a380a076cbe2ad244b9b007fc239`, 2,247,877 bytes. Stable replay: `https://softmax-public.s3.amazonaws.com/replays/e8568e8d-c93f-4c22-af15-94721a5ffade.replay`. Hosted viewer: `https://d1kovwradqjymp.cloudfront.net/bundles/5df3dc2cefda2002b95a6892330cb864f7977f12f117bfa80fff8c65bd75f140/0aeedafa5b1f43caaa4bbd5b968a7ca6/index.html?v=2#replay=https%3A%2F%2Fd1kovwradqjymp.cloudfront.net%2Freplays%2Fe8568e8d-c93f-4c22-af15-94721a5ffade.replay`.
- Candidate replay SHA-256 `17270f4a69342479e43f88d6ad055dbd8c14601c1c6c41b7110fdb4c01c7abc3`, 2,069,189 bytes. Stable replay: `https://softmax-public.s3.amazonaws.com/replays/35eccc26-828a-43be-a238-ce778e413846.replay`. Hosted viewer: `https://d1kovwradqjymp.cloudfront.net/bundles/5df3dc2cefda2002b95a6892330cb864f7977f12f117bfa80fff8c65bd75f140/0aeedafa5b1f43caaa4bbd5b968a7ca6/index.html?v=2#replay=https%3A%2F%2Fd1kovwradqjymp.cloudfront.net%2Freplays%2F35eccc26-828a-43be-a238-ce778e413846.replay`.
- Both replay bytes and results are present in `/opt/data/profiles/softmax-research-demo/cache/scratch/gota-evidence-full/`; the supported CLI manifest records each hash. A download/hash is **not** replay inspection.
- Actual inspection remains incomplete. `coworld replay-open --hosted --no-open-browser` returns the hosted viewer links, but the supported browser harness fails before navigation with `browser-harness: daemon default didn't come up`, log reason `fatal: chrome-not-running: no supported Chromium-family browser is running -- start Chrome, then retry`. A standalone Chromium could start, but the supported browser helper still could not attach; no viewer content or match events were observed. The source-matched native replay extractor (Polyworld source commit above) is unavailable because this host has no Nim/Nimby. The official toolchain setup attempt was blocked by the execution guard; per user instruction it was not retried or bypassed. Do not describe either replay as inspected.

## Hypothesis and verdict

Hypothesis: increasing visible-enemy-hero target score from +60 to +100 may improve nearby skirmishes/Glory; counter-hypothesis: it diverts pressure from lanes/objectives. **Verdict: inconclusive; descriptive XP movement, not improvement.** Candidate slot 0 had +318 XP, but both teams timed out, all official scores were zero, and score-relevant behavior could not be checked in the replays. One run per arm is underpowered; seat/team/seed interactions remain confounds. The candidate did execute without an episode error, but that is functional smoke evidence, not evidence that it wins.

## Completion and remaining gap

Completed: two authorized requests; terminal results collected; replay and result artifacts downloaded and hashed; actual metrics compared; baseline/candidate source and immutable uploaded-version IDs matched from episode participants; report and iteration record pushed to the research repository. A credential-free, offline-validated evidence bundle is in `docs/reports/gota-evidence/` and includes official request/participants/results snapshots, exact request bodies, replay hashes, and the exact historic setup-guard denial plus corrected upstream installation path. Bundle commit: `a901389` (full commit on branch `agent/hermes-gota-20261006`). Policy code commit remains `856984c58692163e23ee7aa5826a2b180742b3bb` in the pushed policy branch. Incomplete: actual replay inspection/native event decode; current toolchain/bootstrap correction is documented but not executed. No league submission, new request, further research iteration, or policy-strength claim.
