# Working context

## Current objective

Complete the authorized single GOTA iteration: source-matched baseline and one-change candidate, each uploaded and privately evaluated in one normal ten-seat episode. Explicit `policy_ref` versions may be used without league submission. Maximum two experience requests total, existing credits only, no refill, league submission, elevated/owner/alternate-user auth, or background scheduling. Persist keys before create; record IDs immediately; reconcile uncertainty before retry. Budget cap $10 total Nous spend. Baseline `hermes-gota-iteration:v1` and candidate `hermes-gota-iteration:v2` have both uploaded. Candidate source commit `856984c58692163e23ee7aa5826a2b180742b3bb` contains actual `policy.bas` change `+60` to `+100` enemy hero preference; SHA-256 `f29640c1c2179795d8154d7ece9b5595b5a76024f49166745af152d3af5f1dee`.

Rohit approved that baseline spend ask and explicitly authorized dailyCredits=100 ($10/day); retain it unchanged. History was reconciled empty before retry. Reused exact baseline body/key, creating baseline xreq `xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39` and episode request `ereq_19048656-ae8c-4793-8b71-fc17554719e4` (pending at create). Cost preview 0.5 credits; roster resolved ten requested policies, seed 2026, max_ticks 28800, Open Draft. This is created request 1 of max 2. Next wait for completion, download and inspect; only then reconcile history and use the exact saved candidate body/key if no existing candidate request. No league submission or credit/credential changes.

Baseline terminal: xreq `xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39` completed one episode without error, results outcome `time_limit`, all ten official scores 0, 28,909 ticks, seat 0 XP 1,609. Replay artifact downloaded (SHA-256 `bc1938b6ecf37f27ab75488e37753c9dd305a380a076cbe2ad244b9b007fc239`); hosted viewer link obtained. Replay not yet inspected: hosted browser daemon reports no Chrome process; native extractor needs Nim 2.2.10 / Nimby, absent here. An installation setup command was blocked by execution guard; do not reissue or bypass it. Candidate now authorized by blanket spend policy; reconciled history showed only baseline, then exact saved body/key created xreq `xreq_5c2a0c44-f187-4064-9c50-23154038c4c2`, ereq `ereq_385ae031-a7ea-40a9-a384-dd0cb0f453c6`, v2 policy UUID `a93a31e0-c047-4e3f-8624-f4bdeeef901f`. Created requests 2/2. Candidate replay inspection still required if feasible without blocked setup; otherwise report exact blocker and don't claim inspection. DailyCredits=100 retained as user-directed; no league submission.

Previous baseline XP create attempts used the exact same persisted key/body and each returned HTTP 403, exact detail: “Your coach has not chosen a league for this cogent yet; ask them to pick one in the IDE.” Platform operation IDs `5dc12f0d-41cd-4a8a-9391-ce2d3278e9e8` and `6846aa8d-1516-412c-8615-633d8a807312`; no xreq/episode existed at that earlier checkpoint. The user-authorized bounded GOTA iteration and no-league-submission condition apply only to this active task; exact authorization is in `user_preferences.md` and the durable iteration report.
 Do not conflate unrelated `/observatory/players` list denial with XP creation. No eval/replay/verdict yet. Before any create retry, reconcile this exact key in request history; same immutable body/key only if no existing request. No elevated auth or membership submission as a workaround.




## Active games

GOTA setup pending. Policy repository: https://github.com/Metta-AI/rohit-gota-policy.
GOTA binding installed in games/gota. League identity, current game revision and live execution remain unverified.

## Open threads

Install both private repositories on the existing Hermes instance through supported Git authentication.
Load these instructions and skills, then verify a recorded file and both Git revisions after restart.
The Softmax backend integration is separate work; the earlier laptop bridge was temporary.

## Identity

Softmax player: ply_305f0175-65a2-47ca-9566-69991871b743.
Hermes instance: softmax-ide-test; durable chat session: 20261005_232250_b09ac9.

## Harness wiring

Not installed yet. Follow harness/README.md and harness/other/README.md.
Use native Hermes hooks where supported; record verified wiring rather than assuming hooks run.
The seed's documented checklist fallback is available if no compatible hook exists.

## Policy ownership

Policy source and VERSION_LOG.md belong to the separate policy repository.
Research records belong here and cite immutable policy commit IDs.
Multiple agents will use independent checkouts and branches. Only one agent is in scope now.
