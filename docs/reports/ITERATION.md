# Iteration handoff — 2026-10-06

Status: discovery and one inert baseline upload complete. No hosted episode was submitted, so there are no request, episode, or replay IDs. Blocker: the authenticated scoped player identity has no permission to create/upload policy resources required for an experience request; it returns HTTP 403. No broader credential or fallback identity will be used.

## Scope authorized by Rohit

> Autonomy is authorized for one complete bounded GOTA policy-development iteration: discovery, leaderboard access, baseline policy build/upload and one-seat 10-seat normal episode, one attributable candidate change, candidate upload/evaluation (one episode), replay download and actual inspection, performance analysis, and agent-owned Git pushes to both repositories. Maximum two experience requests, one normal 10-seat episode each; existing credits only; no credit grants/refills, league submission, or background scheduling. Persist each idempotency key before submission and request/episode IDs immediately after; reconcile any uncertain request before any retry. Overall Nous spending cap $10 including setup. Do not pause between authorized steps. If a real auth/credit/platform boundary blocks evaluation, do not bypass it; complete independent discovery, code/report/push work and report the exact blocker.

## Verified setup / league

- Research checkout initially at user-provided `75884d9`; policy checkout initially at `eab20515724dc0ea63ce13551333a155c81f7ce3`. Both writable checkouts use agent-owned branch `agent/hermes-gota-20261006`; no other agent files were overwritten.
- CLI `coworld 0.1.57`; `softmax status` authenticated the expected player `ply_305f0175-65a2-47ca-9566-69991871b743`.
- Active target: GOTA Competition, league `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`, division `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`, Coworld `cow_162aa34f-f447-4c5d-8db3-480ec83e98f4`, release `2026.10.6.1`.
- Release source Polyworld ref `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`; source-matched base file SHA-256 `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`.
- Current board: a-aron MMR 29.97/mean 65.42 (33 rounds); Aaron 26.30/43.59 (44); BeWellBot v58 25.61/42.64; richard v340 24.55/28.63; khors v231 23.50/33.11; fly_brain v1 22.33/32.72. Existing champion `arena-crossbow-carry:v33` rank 40, MMR 13.20/mean 1.10 (43 rounds). Board MMR and mean score are distinct metrics.

## Upload and auth blocker

- Uploaded `hermes-gota-iteration:v1`, unmodified baseline `policy.bas`; CLI response was `Upload complete: hermes-gota-iteration:v1`. Upload command output did not return a version UUID. Baseline source commit is `eab20515724dc0ea63ce13551333a155c81f7ce3`; its SHA matches the hosted reference exactly.
- `coworld memberships --mine` for uploaded `hermes-gota-iteration:v1` returned no league membership. GOTA policy not submitted (submission not authorized).
- `coworld xp-request list --mine` succeeded and was empty before eval. Roster-resolution or player-list APIs were attempted only as read calls; `/observatory/players` is explicitly denied for this credential with HTTP 403 (request IDs `8c923c78-3756-4175-ae72-167568534029`, `0ea2cca1-c290-450b-a367-51385a69cc44`).
- Current CLI help and live manifest establish experience requests need explicit `policy_ref` seats in a ten-player roster. CLI auth principal is the intended scoped PLAYER. No policy-membership creation route is available on the PLAYER auth: membership/submission management is forbidden to it. The normal create path must not be bypassed by using a user/owner credential, changing identities, or promoting the policy to the competition.
- One preserved baseline request template and key (not submitted): `gota-baseline-request.json`, idempotency key `hermes-gota-20261006-baseline-58cce3a6-ff1a-436b-9a4d-99c3e6da513b`.
- Candidate request template/key also preserved but not submitted: `gota-candidate-request.json`, key `hermes-gota-20261006-candidate-9b899046-78cb-47b4-a1b6-bed2fefeda9d`. It references `hermes-gota-iteration:v2`, which was not uploaded. Neither key has been transmitted; these scratch bodies can be regenerated if setup resumes.

## Candidate and hypothesis

Candidate is one score-weight change at `policy.bas` line 201: visible enemy-hero preference `+60` becomes `+100`; no other change. Hypothesis: strengthen target selection toward enemy heroes in nearby skirmishes to improve team outcome and Glory; the alternative is diversion from lane/objective pressure. One normal full-length episode per version was preplanned against identical pinned ten-seat roster, slot positions, Open Draft, seed 2026, and `max_ticks: 28800`. Precommitted screen: candidate wins/better score => directional support only; any other or tainted comparison => inconclusive. Two episodes cannot establish strength. Candidate was not uploaded because evaluation authorization depends on an inaccessible league membership.

## Pending

- No experience-request POST executed; no request or episode IDs; no replay to inspect; no performance verdict.
- Need an authorized GOTA competition membership for `hermes-gota-iteration` in the stated division (without league submission by this agent) or explicit platform grant of the minimal create/experiment permission to the PLAYER identity.
- Next action only after authorized identity/membership is available: verify visibility/readback, upload one-change `v2`, persist exact idempotent request key/body before POST, submit only after baseline has valid roster eligibility, immediately log returned request/episode IDs, run both episodes serially under existing credits, retrieve/inspect actual replay events, and close hypothesis record.
