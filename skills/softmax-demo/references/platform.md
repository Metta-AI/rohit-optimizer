# Supported Softmax workflow — 2026-10-06

Use the published Coworld CLI, pinned in the research repository's pyproject.toml/uv.lock.
Run from that repository with `uv run --frozen coworld ...`. Python 3.12 is required; Hermes's own Python can differ.
`uv sync --frozen` installs the environment without a private Metta checkout. Git and uv must be on PATH.
Use the official uv installation guide if absent: https://docs.astral.sh/uv/getting-started/installation/ .

## Credentials

The provisioning service supplies a revocable PLAYER credential as a private runtime file, and expected player ID.
Run `uv run --frozen python skills/softmax-demo/scripts/configure_auth.py --token-file /run/secrets/softmax-player --player PLAYER_ID --config-dir /opt/data/softmax-auth`.
Export `SOFTMAX_CONFIG_DIR=/opt/data/softmax-auth` for every command. Keep this directory outside both repositories.
The helper verifies the principal before saving through softmax.auth. Never paste credentials into prompts or command arguments.
GitHub: use the supported `gh`/Git credential helper with an authorized account, or a repository-scoped GitHub App token supplied by the provisioner.
The agent needs read/write on its research and policy repositories, and read access to Polyworld source/assets for native replay inspection.
No credentials are bundled with the distribution. Missing access is a setup failure, not permission to borrow a broader token.

## Discovery and standings

```
uv run --frozen softmax status --server https://softmax.com/api
uv run --frozen coworld leagues --json
uv run --frozen coworld leagues LEAGUE_ID --json
uv run --frozen coworld divisions --league LEAGUE_ID --json
uv run --frozen coworld results DIVISION_ID --json
uv run --frozen coworld show COWORLD_ID --json
```

Record the actual GOTA league, division, release, manifest and participation guide. Names are not stable identifiers.
Save leaderboard JSON with a timestamp. Interpret the division's rating and mean score separately.
Live API schema: https://softmax.com/api/observatory/openapi.json . The CLI server is https://softmax.com/api;
the HTTP client maps Observatory routes correctly. Do not use the seed's old server-key credential fallback.

## Upload

GOTA uses game-hosted BASIC file policies. Read the live manifest's player protocol before building.
Use the source matching that release, not an unverified main-branch baseline.

```
uv run --frozen coworld upload-policy --file /absolute/policy.bas --name POLICY_NAME --title "Baseline smoke" --description "Pinned GOTA baseline; functional validation only"
```

Read command help for accepted flags. Save output and policy version ID immediately. Hash the source bytes and record the source commit.
No Docker image is needed for a BASIC file policy. A successful upload does not prove the policy executes.

## Bounded evaluation

Use `coworld xp-request create --help` and the live V2CreateExperienceRequestRequest schema to construct a valid JSON body.
Prefer the live league's documented roster/configuration; freeze opponent policy version IDs and slot assignments.
For the first iteration, run one baseline smoke and one candidate smoke, one episode each, serially, once the operator confirms the run budget. Do not expand automatically.
Write the hypothesis before modifying one policy behavior. Preserve all ten seats and normal game limits.

```
uv run --frozen coworld xp-request create request.json --title "GOTA smoke" --description "One bounded policy validation episode" --json
uv run --frozen coworld xp-request get XREQ_ID --json
uv run --frozen coworld xp-request episodes XREQ_ID --view results --json
uv run --frozen coworld xp-request watch XREQ_ID --until evidence --include replay --include results --checkpoint .runtime/watch.json --timeout 3600
uv run --frozen coworld xp-request download XREQ_ID --include replay --include results --directory .runtime/evidence
```

The current API supports idempotency_key. Generate one per immutable request body and persist both BEFORE submission.
On a lost response, reuse the identical body and key; never issue a replacement key for the same intended experiment.
Persist the returned request ID immediately. If the deployed server rejects this contract, stop and report it.
A 401/403 is an identity/permission failure; 402 is exhausted credit. Do not grant credits, change budgets, or switch to owner credentials.
Inspect downloaded manifests for availability and errors. Never interpret a failed episode as a policy loss.
Use `coworld episodes --help` for inspection subcommands and `coworld replay-open --help` for hosted viewer links.

## Evidence and Git

The agent itself writes docs/reports/ITERATION.md with: league/division, game version, source commits/checksums,
upload versions, request/episode IDs, replay links/checksums, actual inspected events, scores by seat/team, limitations,
and the hypothesis verdict. Inspect both baseline and candidate. Two smoke episodes cannot establish a reliable win.
Record version provenance in the policy repository's VERSION_LOG.md. Push both repositories to agent-owned branches.
Record exact pushed commit IDs, not just branch names. Do not include signed download URLs or credentials in Git;
use stable Softmax episode/replay links and artifact IDs. Preserve failed/inconclusive reports as well as winners.

## Request template

Create ten roster entries with unique slots 0 through 9, each player containing exactly one policy_ref.
For a controlled smoke, use the candidate in one fixed seat and nine pinned reference/opponent versions.
Use the same configuration, roster seats and seed (where the live game schema supports it) for baseline and candidate.
Body fields: target={"league_id": "the resolved league ID"}, roster=[{"slot":0,"player":{"policy_ref":"name:v1"}}, ...],
num_episodes=1, idempotency_key="a persisted unique key", private=true, title and description.
The ellipsis is explanatory, never valid JSON. Derive actual IDs from discovery; do not submit placeholders.
The roster schema is bundled as request-schema.json for offline validation, captured 2026-10-06; refresh if the server contract changes.
