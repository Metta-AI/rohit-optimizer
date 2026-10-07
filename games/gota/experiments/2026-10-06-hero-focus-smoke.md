# GOTA iteration record — 2026-10-06

Status: the two authorized one-episode requests completed without episode errors. Both timed out with zero official scores in all ten seats. Candidate slot 0 earned 1,927 XP versus baseline 1,609 (+318), but XP is descriptive only, not evidence of improvement. Replays were downloaded and hashed; actual replay inspection is incomplete because the supported browser harness could not attach to Chromium and this host lacks Nim/Nimby for the source-matched extractor.

## Authorized scope

One baseline and one candidate, one normal ten-seat episode each; max two experience requests total; existing credits only; no refills, league submissions, or background work. Overall Nous cap: $10 including setup. Both immutable request bodies/idempotency keys are saved under the profile scratch path, created after history reconciliation. All authorized requests are used. No new request or further iteration.

## Live discovery

- CLI: `coworld 0.1.57`; authenticated subject player `ply_305f0175-65a2-47ca-9566-69991871b743`.
- Competition league `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`.
- Coworld `cow_162aa34f-f447-4c5d-8db3-480ec83e98f4`, live release `2026.10.6.1`, full-game 28,800 tick cap, Open Draft, ten BASIC seats.
- Hosted source ref: Polyworld `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`; hosted `base.bas` SHA-256 `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`, same as policy v1 source.

## Strategy and pre-registration

Question: does a modestly stronger visible-enemy hero preference help the reference policy convert nearby skirmishes into wins/score?

Single candidate change: in `policy.bas` enemy hero target score bonus increases from `+60` to `+100` (only the existing branch for visible enemy heroes within 18 tiles). No other behavior changes.

Mechanism: a larger score increment can make a visible hero more likely to be targeted rather than a nearby creep/building. This may improve skirmishes, or divert pressure from lane/objective progression.

Predictions: if beneficial, candidate should improve team outcome/score against the same pinned roster/seed; if not, it fails to improve or reduces the outcome. Decision rule: one episode per arm is directional only; infrastructure-tainted results are excluded; no policy-strength claim from this sample.

Adversarial critique: N=1 per arm has negligible statistical power; the team seat and single seed can dominate; result and replay behavior must be distinguished. Replay analysis could not be completed, so mechanism-level evidence is absent.

## External-operation checkpoint ledger

- Discovery: live identity, league/release/schema/leaderboard read.
- Baseline upload: `hermes-gota-iteration:v1`, source commit `eab20515724dc0ea63ce13551333a155c81f7ce3`, source SHA-256 `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`.
- Candidate upload: `hermes-gota-iteration:v2`, policy source commit `856984c58692163e23ee7aa5826a2b180742b3bb`, source SHA-256 `f29640c1c2179795d8154d7ece9b5595b5a76024f49166745af152d3af5f1dee`; change +60→+100 only.
- Earlier baseline attempts before the resumed successful run were denied HTTP 403 twice with the same saved baseline key; exact detail and denied-operation IDs are preserved in the report history. They created no xreq and are not counted as new successful requests.
- Resumed baseline create: after verifying request history and reusing the exact persisted baseline body/key, created `xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39`, episode `ereq_19048656-ae8c-4793-8b71-fc17554719e4`, initially pending; one ten-seat episode, seed 2026, max 28,800 ticks, Open Draft.
- Baseline terminal: `outcome=time_limit`, `ticks=28909`, `scores=[0,0,0,0,0,0,0,0,0,0]`, `total_xp=[1609,5078,6360,4262,3630,1866,5931,2074,2032,3699]`; seat 0 score 0/XP 1,609. No error; ten scripts active. Red/Blue towers remaining 9/5; gods each 400 HP.
- Reconciled request history showed baseline only before candidate; reused exact saved candidate body/key, creating `xreq_5c2a0c44-f187-4064-9c50-23154038c4c2`, episode `ereq_385ae031-a7ea-40a9-a384-dd0cb0f453c6`; candidate version UUID `a93a31e0-c047-4e3f-8624-f4bdeeef901f`. This is request 2/2.
- Candidate terminal: `outcome=time_limit`, `ticks=28909`, `scores=[0,0,0,0,0,0,0,0,0,0]`, `total_xp=[1927,6882,6254,5647,2403,1719,3938,2218,3902,1641]`; seat 0 score 0/XP 1,927. No error; ten scripts active. Red/Blue towers remaining 7/6; gods each 400 HP.
- Immutable participant version UUIDs: baseline `e1d160b8-a9b9-4a78-8295-e529257cdab8`; candidate `a93a31e0-c047-4e3f-8624-f4bdeeef901f`. Job/replay identifiers: baseline `e8568e8d-c93f-4c22-af15-94721a5ffade`; candidate `35eccc26-828a-43be-a238-ce778e413846`.
- Replay evidence is cached in `/opt/data/profiles/softmax-research-demo/cache/scratch/gota-evidence-full/`; baseline SHA-256 `bc1938b6ecf37f27ab75488e37753c9dd305a380a076cbe2ad244b9b007fc239`, candidate SHA-256 `17270f4a69342479e43f88d6ad055dbd8c14601c1c6c41b7110fdb4c01c7abc3`. Stable replay links and viewer links are in `docs/reports/ITERATION.md`.
- Inspection boundary: supported `coworld replay-open --hosted --no-open-browser` produced viewer links. Supported Browser Use failed before navigation: `browser-harness: daemon default didn't come up`; log: `fatal: chrome-not-running: no supported Chromium-family browser is running -- start Chrome, then retry`. A standalone Chromium instance started, but the supported browser tool still failed to attach; no replay content was viewed. Native source-matched replay extractor unavailable: `nim` and `nimby` are absent. Its official setup attempt was blocked by the execution guard and, as directed, was not retried or bypassed. Thus replay inspection is explicitly incomplete.
- Comparison: candidate seat 0 XP +318; aggregate Red XP 23,113 vs 20,939 (+2,174), Blue 13,418 vs 15,602 (−2,184), tower counts differ, yet both outcomes and every official score are identical (timeout/zero). Team, role, map/seed and opponent effects are not controlled by the single changed policy seat.
- Git: policy code commit `856984c58692163e23ee7aa5826a2b180742b3bb` remains on pushed policy branch `agent/hermes-gota-20261006`. Current iteration report updated for push on research branch `agent/hermes-gota-20261006`.

## Verdict

**Inconclusive; no demonstrated improvement.** Candidate executed successfully as a hosted smoke, but both episodes timed out with all ten official scores zero. Candidate slot 0 XP rose by 318, but replay inspection is incomplete and XP alone cannot establish a win, causal effect or performance gain. One episode per arm is underpowered; seat/team and match variation confound the comparison. No league submission or additional research iteration was made.
