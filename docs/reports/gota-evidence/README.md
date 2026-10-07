# GOTA evidence-bundle validation

This is a credential-free source snapshot for the two completed GOTA smoke requests. It contains no authorization headers, access tokens, replay bytes, or signed download URLs. The request bodies include the exact idempotency keys used at creation and are for audit only; do not resubmit them.

Files include exact request bodies, official request and episode/participant results, raw game result artifacts, and replay/result artifact hashes, plus the exact historic setup-guard denial. See the contents and provenance below.

## Offline validator

Run `python3 docs/reports/gota-evidence/verify.py` from the repository root. It checks JSON integrity, request→episode IDs, idempotency keys, immutable policy versions, ten participants and scores per arm, raw result arrays, and replay/result manifest entries. It also rejects common credential markers. It intentionally does not treat hashes or manifest rows as proof of replay inspection.

## Files

- `baseline-request-body.json`, `candidate-request-body.json`: exact saved JSON request bodies used for the authorized requests.
- `baseline-request.json`, `candidate-request.json`: official `coworld xp-request get --json` responses; include request lifecycle and platform-resolved episode/participant metadata. Requester identity fields were removed.
- `baseline-results-and-participants.json`, `candidate-results-and-participants.json`: official `coworld xp-request episodes <xreq> --view results --json` responses; one episode each, including ten participants and scores.
- `baseline-results.json`, `candidate-results.json`: raw game-produced result artifacts.
- `replay-manifest.json`: official artifact manifest rows for replay and result files, including artifact ID, version, size, SHA-256, and state. Replay binaries remain in profile scratch, not Git.
- `toolchain-setup-blocker.md`: exact previously blocked setup command and exact execution-guard response, recovered from the prior session record.
- `verify.py`: offline integrity/sanitization check.

Source run: Gods of the Arena release `2026.10.6.1`, hosted Polyworld source commit `5287c437fe5e4ae7a1fc56df3fa40f6821a7d5fd`. Baseline request `xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39`; candidate request `xreq_5c2a0c44-f187-4064-9c50-23154038c4c2`. Both ran a normal ten-seat single episode with pinned opponents, seed 2026, Open Draft and `max_ticks=28800`.

Run `python3 -m json.tool <file> >/dev/null` on any JSON file if only syntax validation is needed. The verifier makes no network calls or evaluations. Verify replay bytes against the manifest only when those bytes are available; a matching hash does not mean the replay was inspected.

`toolchain-setup-blocker.md` distinguishes the blocked Nim binary download/extraction command from the earlier runbook script's Python-package resolver failure (`uv tool install nimby` versus the runbook's Nimble-based Nimby install). No evaluation or replay-toolchain setup command is run by this validation.
