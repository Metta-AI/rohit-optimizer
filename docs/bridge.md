# Softmax IDE bridge

The distribution owns `plugins/softmax`: the Hermes platform adapter and the chat/research bridge.
Hermes discovers the enabled `softmax` plugin from the installed profile and owns its lifecycle.
There is no detached startup hook or second supervisor.

## Provision an instance

1. Install this repository with `hermes profile install <repository> --name optimizer --yes`.
2. Supply `API_SERVER_KEY` in the installed profile's `.env` with mode 0600.
3. Create `softmax-bridge/config.json` beneath that profile's Hermes home, with mode 0600:

```json
{
  "player_id": "<player ID>",
  "agent": "<registered agent name>",
  "session_id": "<stable coach session ID>",
  "softmax_url": "<Softmax Observatory API base URL>",
  "hermes_url": "http://127.0.0.1:8642/",
  "player_token": "<scoped Softmax cogent-agent token>",
  "service_key": "<same value as API_SERVER_KEY>"
}
```

4. Run `python -m pm.cli install --extra messaging` in the Hermes installation environment to prepare the API dependencies.
   The profile already enables the plugin; `hermes -p optimizer plugins enable softmax` verifies that selection.
5. Start the configured profile with `hermes -p optimizer gateway run` under the instance's supported supervisor.

Do not start a second gateway beside an existing host gateway. These commands describe a new, stopped runtime;
Nous's configuration-triggered restart defect is not repaired by this distribution.

`bundle_id` may be supplied by provisioning to enable readiness callbacks. `workspace` may identify an existing
autoresearch workspace for inbox/outbox forwarding. Neither is needed for standalone chat bridging.
State and credentials under `softmax-bridge/` are deployment-owned and excluded from distribution updates.
The plugin writes the scoped CLI credential into the runtime user's `.softmax/credentials.yaml`.

Profile installation copies files; it does not execute setup scripts or mint credentials.
Existing profiles retain config on update: explicitly enable `plugins.enabled: [softmax]`,
`gateway.softmax.enabled: true`, and `gateway.api_server.enabled: true` when upgrading.
The API listener must stay on loopback port 8642, as configured for fresh installs.

Bridge implementation originates from Metta commit 55bd534d9d4bdbfbd586c46a7dc5e4e2ae3fbb89.
This change packages that implementation; switching Metta provisioning from file uploads to this distribution is separate work.

## Validation

Run `python -m pytest tests -q` with pytest, pytest-asyncio, httpx, and pydantic installed.
After installing into a clean Hermes runtime, run `tests/smoke_hermes_distribution.py` with
`HERMES_HOME` set to the new profile. This checks real plugin discovery, rejects missing configuration,
and verifies the adapter's profile-local state path. The smoke check creates an empty test config;
use a disposable profile, not a configured instance. It does not test a live model response.
