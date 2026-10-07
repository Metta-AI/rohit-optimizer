#!/usr/bin/env python3
"""Offline integrity checks for the committed GOTA smoke evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "baseline": {
        "xreq": "xreq_d9cbbf96-a43b-4366-98c0-53c48fd68a39",
        "ereq": "ereq_19048656-ae8c-4793-8b71-fc17554719e4",
        "version": "e1d160b8-a9b9-4a78-8295-e529257cdab8",
        "uuid": "hermes-gota-20261006-baseline-58cce3a6-ff1a-436b-9a4d-99c3e6da513b",
    },
    "candidate": {
        "xreq": "xreq_5c2a0c44-f187-4064-9c50-23154038c4c2",
        "ereq": "ereq_385ae031-a7ea-40a9-a384-dd0cb0f453c6",
        "version": "a93a31e0-c047-4e3f-8624-f4bdeeef901f",
        "uuid": "hermes-gota-20261006-candidate-9b899046-78cb-47b4-a1b6-bed2fefeda9d",
    },
}


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> None:
    json_files = sorted(ROOT.glob("*.json"))
    for path in json_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        text = path.read_text(encoding="utf-8").lower()
        for forbidden in ("authorization:", "bearer ", "access_token", "refresh_token"):
            assert forbidden not in text, f"sensitive-looking field {forbidden!r} in {path.name}"
        if path.name.endswith("request-body.json"):
            for key in data:
                assert not any(word in key.lower() for word in ("auth", "token", "header")), (path.name, key)

    for arm, expected in EXPECTED.items():
        body = load(f"{arm}-request-body.json")
        request = load(f"{arm}-request.json")
        episode_page = load(f"{arm}-results-and-participants.json")
        raw_result = load(f"{arm}-results.json")
        entries = episode_page["entries"]
        assert len(body["roster"]) == 10
        assert body["num_episodes"] == 1
        assert body["idempotency_key"] == expected["uuid"]
        assert request["id"] == expected["xreq"]
        assert request["status"] == "completed" and request["completed_count"] == 1
        assert len(entries) == 1
        episode = entries[0]
        assert episode["id"] == expected["ereq"]
        assert episode["experience_request_id"] == expected["xreq"]
        assert episode["status"] == "completed" and episode["error"] is None
        assert len(episode["participants"]) == len(episode["scores"]) == 10
        assert [p["position"] for p in episode["participants"]] == list(range(10))
        assert episode["participants"][0]["policy_version_id"] == expected["version"]
        assert len(raw_result["scores"]) == len(raw_result["total_xp"]) == 10

    manifest = load("replay-manifest.json")
    assert len(manifest["artifacts"]) == 4
    for episode_id in (EXPECTED["baseline"]["ereq"], EXPECTED["candidate"]["ereq"]):
        replay = [x for x in manifest["artifacts"] if x["episode_request_id"] == episode_id and x["filename"] == "replay.replay"]
        result = [x for x in manifest["artifacts"] if x["episode_request_id"] == episode_id and x["filename"] == "results.json"]
        assert len(replay) == len(result) == 1
        assert replay[0]["state"] == result[0]["state"] == "completed"
        assert len(replay[0]["sha256"]) == 64

    print(f"PASS: {len(json_files)} JSON files parse; both request/episode links, idempotency keys, immutable versions, 10 participants/scores, raw results, and four replay/result manifest rows validate; no auth/token markers found.")
    print("Replay inspection status: not asserted by this artifact validator; manifest/hash presence is not replay inspection.")


if __name__ == "__main__":
    main()
