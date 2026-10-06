# GOTA iteration report — 2026-10-06

## Status

Discovery and leaderboard access completed. Source-matched baseline upload `hermes-gota-iteration:v1` and the one-change candidate upload `hermes-gota-iteration:v2` both succeeded. The preserved baseline experience-request create was attempted twice with the exact same body and idempotency key. Both calls returned HTTP 403: `Your coach has not chosen a league for this cogent yet; ask them to pick one in the IDE.` Denial request IDs were `5dc12f0d-41cd-4a8a-9391-ce2d3278e9e8` (first call) and `6846aa8d-1516-412c-8615-633d8a807312` (second call). No experience request or episode was created. The second attempt was made only after `xp-request list --mine` again returned empty, and it reused the identical body/key; no new key was created. This is direct evidence of the XP-create response, not inferred from an unrelated read-only player-list error. User clarifies explicit private `policy_ref` evaluation need not require league submission; therefore the returned league/cogent message is recorded literally and any internal prerequisite interpretation remains unverified.

Candidate source is committed and successfully uploaded as `hermes-gota-iteration:v2`; it has not been evaluated. No episode/experience-request ID, replay, actual replay inspection, evaluation result, or competitive-performance verdict exists. No league submission, alternate account, elevated mode, or owner credentials were used. The hypothesis verdict is **inconclusive / not run**. No winning-policy claim.

## Scope and caps

Rohit authorized one bounded iteration: at most two experience requests, one normal ten-seat episode per request, existing credits only, no credit grants/refills, no league submission, no background work; persist keys before POST and IDs immediately after; $10 Nous spending cap; proceed autonomously and stop only at a real platform/auth/credit boundary. Actual XP create attempts: one (baseline); denied before a request was created. No duplicate or retry was made.

## Discovery

- Player identity from `softmax status`: `ply_305f0175-65a2-47ca-9566-69991871b743`.
- GOTA Competition league: `league_3c60897b-25cf-4b37-9d1a-8554c1198f28`; division: `div_a4534073-c5d2-4193-a94a-93d9c5e2e443`; Coworld: `cow_162aa34f-f447-4c5d-8db3-480ec83e98f4`; release `2026.10.6.1`.
- Game is 5v5, ten BASIC seats; normal full match cap 28,800 ticks and Open Draft. Result includes per-seat score/total XP; winner-only Glory is distinct from ladder rating.
- Hosted source: Polyworld `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`. Imported baseline `policy.bas` SHA-256 is `044f61ada174e477b18562b4b806770545c82b4f1a20aaf65762b880f54424c1`, matching hosted source.
- Competition board snapshot: a-aron rank 1 MMR 29.97, mean score 65.42 (33 rounds); Aaron rank 2 MMR 26.30, mean 43.59 (44); BeWellBot-Arena:v58 rank 3 MMR 25.61, mean 42.64 (44); richard-gods-of-the-arena:v340 rank 4 MMR 24.55, mean 28.63 (44); khors:v231 rank 5 MMR 23.50, mean 33.11 (44); fly_brain:v1 rank 7 MMR 22.33, mean 32.72 (44). Our existing champion `arena-crossbow-carry:v33` ranked 40 with MMR 13.20 and mean score 1.10 (43 rounds). MMR is not mean score.

## Source and upload provenance

- Baseline upload response: `Upload complete: hermes-gota-iteration:v1`. CLI gave the label but no immutable policy-version UUID.
- Baseline source commit: `eab20515724dc0ea63ce13551333a155c81f7ce3`, original source bytes unchanged.
- Candidate source commit: `856984c58692163e23ee7aa5826a2b180742b3bb`, changed one score weight in `readObject(index)`, enemy hero preference `+60` → `+100`; `policy.bas` SHA-256 `f29640c1c2179795d8154d7ece9b5595b5a76024f49166745af152d3af5f1dee`. Commit contains the actual candidate source plus provenance/version-log edits, verified with `git show HEAD:policy.bas` and `git show --stat`.
- Candidate upload response: `Upload complete: hermes-gota-iteration:v2`; no immutable policy-version UUID in CLI output.
- Policy repo branch: `agent/hermes-gota-20261006`; latest pushed candidate source commit above.

## Experiment request

`coworld xp-request list --mine` was empty before first create; after user audit, a second create attempt was made with the **same saved request body and key**, after checking that list remained empty. Both create attempts returned HTTP 403: `Your coach has not chosen a league for this cogent yet; ask them to pick one in the IDE.` Platform operation IDs (not created xreq IDs): `5dc12f0d-41cd-4a8a-9391-ce2d3278e9e8` and `6846aa8d-1516-412c-8615-633d8a807312`. No xreq or episode exists. This is direct evidence only about the XP-create calls. Earlier `coworld player list`/`/observatory/players` 403s were unrelated account-list permissions and were initially overgeneralized; see the corrected current scope in user_preferences.

The candidate request key (`hermes-gota-20261006-candidate-9b899046-78cb-47b4-a1b6-bed2fefeda9d`) was preserved but not submitted. Candidate policy version v2 did upload successfully. Candidate XP create was not attempted after the baseline create returned 403, to avoid consuming another request without a platform-configuration correction.


## Hypothesis and limits

**Hypothesis verdict: inconclusive / not run.** Raising visible-enemy-hero preference from +60 to +100 could increase focus on nearby hero skirmishes, potentially reducing enemy damage and improving win/Glory; alternatively, it could divert from lane/objective progress. This is one attributable source change, but the endpoint denied request creation for both baseline attempts; there are no episode data, so no confirmation, refutation, or performance analysis. A future single episode per version would be only a directional smoke, not a robust policy-strength estimate.

## Incomplete steps / observed blocker

Two baseline XP create attempts were denied HTTP 403 with exact detail `Your coach has not chosen a league for this cogent yet; ask them to pick one in the IDE.` This is the observed create-endpoint response, not an inference from `/observatory/players`. Each attempt returned a platform operation/request ID but no xreq/episode ID; own request listing was empty before each attempt. The second attempt reused the identical persisted key/body after checking history; never retry with a replacement key. The authorized user has clarified explicit private policy_ref lookup should not require league submission, but no test succeeded; the cause behind the text remains unknown. Candidate upload is complete, but no candidate request was attempted. No episodes, replays, replay inspection, or performance analysis exist. To resume after platform/IDE configuration is clarified, first reconcile the original idempotency key in request history, then only retry the same body/key if no matching created request exists; run the already-prepared candidate body within the original two-request limit. No elevated/owner credentials, league submission, refills, or background scheduling.
