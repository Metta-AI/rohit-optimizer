# Autonomous research lifecycle

## Provisioning gate

Install this distribution at an immutable commit into a fresh named profile. Hermes preserves
config on updates; installing updated skills alone does not apply approval settings to old profiles.
Keep private keys, tokens and model-provider credentials outside Git. Use scoped player credentials
and separate repo deploy keys. Resolve models from the provider catalog; never invent a Terra ID.

Before the first objective, run a non-spending acceptance turn through the actual chat/API transport:
create/read a scratch file with Python, invoke a bounded process that times out, resume its recorded
operation, and push a harmless readiness record to the configured agent branch. It must return without
manual approval. Record provider/model, distribution commit, transport, exit status and approval events.
If smart approval escalates, fail readiness. Check the guardian provider and empty-response/timeout
logs. The approval auxiliary task uses the catalog-listed Nous route anthropic/claude-haiku-4.5
with reasoning disabled: the reviewer requests only 16 output tokens. Provisioning must confirm
this route is usable with the mounted provider credentials before starting research. Verify this against the deployed Hermes version; do not silently ignore unsupported config.
Do not disable Tirith, enable YOLO, auto-answer prompts, or add broad shell allowlists to pass the test.

## Execute and recover

The IDE supplies one objective; write it and its bounds to WORKING_CONTEXT.md before doing work.
Record every remote request's idempotency key, payload hash and returned ID before moving to the next
stage. On ambiguous network failure, reconcile the same key/history before any retry. A new chat or
new machine must consult this record, never infer state from missing conversation messages.

Run local build/inspection commands through `scripts/bounded_run.py`. Default limits: 120 seconds,
8 MiB combined output, 64 MiB per generated file, and 512 MiB free disk reserve. Compiler operations
may use a recorded 600-second limit and 256 MiB per file; compile single-threaded. The runner has an
OS lock, atomic state and a two-attempt ceiling. Repeating a completed operation is a read of its
record. `--retry-safe` is only for reproducible local work, never upload/evaluation/submission/push.
Changed inputs or tool revisions require a new operation key. Never put credentials in command args.

After a process failure, inspect its record and bounded log; repair the cause once inside the task's
authorization. After a second failure, mark the objective blocked with the exact boundary and return
one report. Do not keep scheduling the same failure or emitting status pings. Save recovery state after
every completed stage. Raw evidence stays on disk; compact reports and provenance go to Git.

Use supported durable `/v1/runs` for backend lifecycle control where available; persist the run ID and
reconcile status after disconnection. A locked TUI is not the worker protocol. The IDE/backend owns
waking a stopped machine and reconnecting transport; this profile owns checkpoint-based continuation.
Do not claim a profile can restart a powered-off machine. A new agent session should resume the saved
objective without requiring the old terminal or reissuing completed remote work.

## Completion

Return one report with policy commits, request IDs, replay checksums and actual inspection findings,
leaderboard observations, comparison verdict and pushed report links. Resource-limit failures are not
successful analyses. Zero intermediate human approvals is part of the acceptance criteria, alongside
successful recovery of one interrupted local operation and no duplicated remote evaluations.
