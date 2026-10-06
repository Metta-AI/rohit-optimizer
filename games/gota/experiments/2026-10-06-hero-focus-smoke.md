# GOTA iteration record — 2026-10-06

Status: discovery complete, one inert baseline upload done; evaluation is blocked by access boundary before any experience request. Upload completed from source-matched baseline `policy.bas` at original policy commit `eab20515724dc0ea63ce13551333a155c81f7ce3`. Candidate difference prepared but not uploaded. No hosted episodes were submitted, so there are no request, episode, or replay IDs. Scoped player’s roster-resolution/player-list query returned HTTP 403; no stronger credential, league submission, or permission bypass will be used.

## Authorized scope

One baseline and one candidate, one normal ten-seat episode each; max two experience requests total; existing credits only; no refills, league submissions, or background work. Overall Nous cap: $10 including setup. The request idempotency key and immutable body must be written here/on disk before each create call; persist returned request and episode IDs immediately. Never retry an uncertain create without reconciliation.

## Live discovery

- CLI: `coworld 0.1.57` from the locked research environment; authenticated subject is player `ply_305f0175-65a2-47ca-9566-69991871b743`.
- Competition league: `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`.
- Coworld: `cow_162aa34f-f447-4c5d-8db3-480ec83e98f4`, live release **2026.10.6.1**, full-game 28,800 tick cap, Open Draft, ten BASIC seats.
- Hosted source ref: Polyworld `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`; hosted `base.bas` SHA-256 `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`, same as policy checkout `policy.bas`.
- Leaderboard read on 2026-10-06 UTC: current top ten includes a-aron (MMR 29.97, mean game score 65.42, 33 rounds), Aaron (26.30, mean 43.59, 44 rounds), BeWellBot-Arena:v58 (25.61, mean 42.64), richard-gods-of-the-arena:v340 (24.55, mean 28.63), khors:v231 (23.50, mean 33.11), and fly_brain:v1 (22.33, mean 32.72). My existing champion `arena-crossbow-carry:v33` appears rank 40 with MMR 13.20 and mean score 1.10 across 43 rounds. MMR is not mean Glory/game score. Rankings move between reads; saved raw snapshot is under the profile scratch cache, not Git.
- Player identities route `/observatory/players` is denied to this scoped credential (403 request ids recorded in terminal output, no retry attempted); standings, leagues, divisions and memberships did return. No experience requests exist in `xp-request list --mine` at discovery time.

## Strategy and pre-registration

Question: does a modestly stronger visible-enemy hero preference help the reference policy convert nearby skirmishes into wins/score?

Single candidate change: in `policy.bas` enemy hero target score bonus increases from `+60` to `+100` (only the existing branch for visible enemy heroes within 18 tiles). No other behavior changes. The policy still prioritizes low-health enemy heroes and objectives under unchanged scoring rules.

Mechanism: when a vulnerable hero enters target range, the score increment makes the reference agent less likely to choose a nearby creep/building over that hero. If focused pressure denies enemy damage and improves skirmish control, team victory/Emmett’s Glory may improve; if it diverts attacks from lane progression, the result can regress.

Predictions: if true, the candidate will win the one episode and/or produce greater team Glory than baseline against the same pinned roster and game seed. If false, it will lose or fail to improve. Decision rule: one clean episode showing better candidate team outcome/score is only a directional signal; any other or infrastructure-tainted result is inconclusive. Two one-episode requests cannot establish policy strength; any apparent win is not a winning-policy verdict.

Adversarial critique: one episode has negligible statistical power; opponents/roster and seat remain confounds if not pinned identically; a single episode is a screening test for whether the build functions and the intervention looks promising, not a decisive estimate. Compare per-seat/team result and replay events, exclude failures. Human gameplay judgment is limited to the actual inspected replay.

## External-operation checkpoint ledger

- Discovery: live CLI identity confirmed for expected player; league/release/schema/leaderboard read. No uploads or experience requests yet.
- Baseline upload: pending.
- Baseline experience request: pending; no key/request ID yet.
- Candidate upload: pending.
- Candidate experience request: pending; no key/request ID yet.
- Replay retrieval and inspection: pending.
- Git push: pending.
