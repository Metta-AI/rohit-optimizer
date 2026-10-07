# Hermes research distribution

Install this repository at a reviewed immutable commit with `hermes profile install`.
Distribution-owned files are `config.yaml`, `SOUL.md`, `skills/`, and the manifest.
Credentials, workspaces, sessions and memories remain runtime-owned. Config is copied on fresh
installation; Hermes preserves it on ordinary profile updates. Never silently force-config a live agent.

The provisioner supplies the provider/model, scoped Git and Softmax credentials, and repository
locations. `skills/softmax-demo/scripts/bootstrap.sh` installs the locked CLI without spending credits.
`references/autonomy.md` defines readiness, runtime bounds and recovery. Run its acceptance turn
through the same transport used by the IDE before accepting a research task.

For a fresh runtime, use the supported durable Hermes `/v1/runs` API where the installed server
supports it. Keep the run ID and idempotency key outside the chat transcript. Reconnect by reading
the run, not by opening a second TUI. The Softmax backend owns machine wakeup and transport recovery;
the research profile owns on-disk task state, operation limits and reconciliation of remote writes.

For local verification:

```sh
python3 -m unittest discover -s tests -v
```

This profile does not claim provider outages or missing guardian support are recoverable purely
through instructions. The no-human-approval readiness turn must pass before declaring autonomy.
