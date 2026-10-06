#!/usr/bin/env python3
"""Run one isolated local GOTA match through the official file handoff."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
import zlib
from pathlib import Path

LOCAL_PLAYER_ID = "ply_762bc195-556b-4f65-aed3-c17cc4afe660"
SEED = 2026
MAX_TICKS = 28800
SPAWN_INTERVAL_TICKS = 480
SEAT_COUNT = 10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replay_metadata(path: Path) -> dict:
    raw = path.read_bytes()
    first = raw[:256]
    fmt = "unknown-binary"
    payload = raw[:8192]
    if raw.startswith(b"\x1f\x8b"):
        fmt = "gzip"
        try:
            dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
            payload = dec.decompress(raw, 8192)
        except zlib.error:
            payload = b""
    elif raw.startswith(b"PK\x03\x04"):
        fmt = "zip"
    elif raw.lstrip().startswith((b"{", b"[")):
        fmt = "json"
    elif raw.startswith(b"\x89PNG"):
        fmt = "png"
    strings = [s.decode("ascii", "replace") for s in re.findall(rb"[ -~]{4,}", payload[:8192])[:24]]
    parsed = None
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    return {
        "path": str(path),
        "size_bytes": len(raw),
        "sha256": sha256(path),
        "format_from_magic": fmt,
        "magic_hex": first[:32].hex(),
        "decoded_json_prefix": parsed if isinstance(parsed, (dict, list)) else None,
        "ascii_strings_in_prefix": strings,
    }


def run_match(binary: Path, source: Path, out: Path, arm: str, timeout: int) -> dict:
    if out.exists():
        raise FileExistsError(f"Refusing to reuse run directory: {out}")
    out.mkdir(parents=True)
    source_bytes = source.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    staged_dir = out / "staged"
    logs_dir = out / "player-logs"
    staged_dir.mkdir()
    logs_dir.mkdir()
    seats = []
    for slot in range(SEAT_COUNT):
        src = staged_dir / f"slot-{slot}.bas"
        # Candidate controls the identified local player's seat 0; all other
        # seats use the unchanged baseline in both arms.
        if arm == "candidate" and slot != 0:
            # The runner receives the baseline path in GOTA_BASELINE_SOURCE.
            slot_bytes = Path(os.environ["GOTA_BASELINE_SOURCE"])
            bytes_for_slot = slot_bytes.read_bytes()
        else:
            bytes_for_slot = source_bytes
        src.write_bytes(bytes_for_slot)
        log_path = logs_dir / f"slot-{slot}.log"
        seats.append({
            "slot": slot,
            "file_uri": src.resolve().as_uri(),
            "content_hash": hashlib.sha256(bytes_for_slot).hexdigest(),
            "size_bytes": len(bytes_for_slot),
            "log_uri": log_path.resolve().as_uri(),
            "artifact_uri": "",
            "annotations_uri": "",
        })
    config = {
        "tokens": [f"local-seat-{slot}" for slot in range(SEAT_COUNT)],
        "players": [
            {"name": f"{LOCAL_PLAYER_ID} ({arm})" if slot == 0 else f"Baseline {slot}"}
            for slot in range(SEAT_COUNT)
        ],
        "seed": SEED,
        "max_ticks": MAX_TICKS,
        "spawn_interval_ticks": SPAWN_INTERVAL_TICKS,
        "headless_tick_rate": 0,
    }
    seats_doc = {
        "schema": "coworld-player-seats/2",
        "seats": seats,
        "player_status_uri": (out / "player-status.json").resolve().as_uri(),
    }
    config_path = out / "config.json"
    seats_path = out / "seats.json"
    results_path = out / "results.json"
    replay_path = out / "match.replay"
    failure_path = out / "player-failure.json"
    config_path.write_text(json.dumps(config, sort_keys=True, indent=2) + "\n")
    seats_path.write_text(json.dumps(seats_doc, sort_keys=True, indent=2) + "\n")
    with (out / "game.stdout.log").open("wb") as stdout:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        env = os.environ.copy()
        env.update({
            "COGAME_CONFIG_URI": config_path.resolve().as_uri(),
            "COGAME_PLAYER_SEATS_URI": seats_path.resolve().as_uri(),
            "COGAME_RESULTS_URI": results_path.resolve().as_uri(),
            "COGAME_SAVE_REPLAY_URI": replay_path.resolve().as_uri(),
            "COGAME_PLAYER_FAILURE_URI": failure_path.resolve().as_uri(),
            "COGAME_HOST": "127.0.0.1",
            "COGAME_PORT": str(port),
        })
        start = time.monotonic()
        proc = subprocess.Popen([str(binary.resolve())], cwd=out, env=env, stdout=stdout, stderr=subprocess.STDOUT)
        outcome = None
        try:
            deadline = start + timeout
            while time.monotonic() < deadline:
                if results_path.exists():
                    # The protocol publishes results by atomic rename after the
                    # replay and seat logs have been closed. Stop the HTTP host now.
                    proc.terminate()
                    try:
                        proc.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=3)
                    outcome = "results_published"
                    break
                if failure_path.exists():
                    proc.terminate()
                    proc.wait(timeout=8)
                    raise RuntimeError(f"Player failure marker published: {failure_path.read_text()}")
                code = proc.poll()
                if code is not None:
                    raise RuntimeError(f"Game exited with code {code} before results appeared; see {out / 'game.stdout.log'}")
                time.sleep(0.2)
            else:
                proc.terminate()
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
                raise TimeoutError(f"Match exceeded {timeout}s; no results file was published")
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=3)
        elapsed = round(time.monotonic() - start, 3)
    results = json.loads(results_path.read_text())
    if len(results.get("scores", [])) != SEAT_COUNT or len(results.get("total_xp", [])) != SEAT_COUNT:
        raise ValueError(f"Wrong score/XP seat count: {results}")
    if results.get("seed") != SEED:
        raise ValueError(f"Unexpected result seed: {results.get('seed')}")
    if not replay_path.is_file():
        raise FileNotFoundError("Atomic results file appeared without replay")
    status = json.loads((out / "player-status.json").read_text())
    players = status.get("players", [])
    log_checks = []
    for slot in range(SEAT_COUNT):
        log_path = logs_dir / f"slot-{slot}.log"
        text = log_path.read_text(errors="replace") if log_path.exists() else ""
        log_checks.append({
            "slot": slot,
            "bytes": len(text.encode()),
            "started": f"Player slot {slot} started." in text,
            "completed": f"Player slot {slot} completed." in text,
            "basic_error": "BASIC error:" in text,
            "status": players[slot] if slot < len(players) else None,
        })
    rec = {
        "arm": arm,
        "source_path": str(source.resolve()),
        "source_sha256": source_hash,
        "local_player_id": LOCAL_PLAYER_ID,
        "local_candidate_seat": 0 if arm == "candidate" else None,
        "configuration": config,
        "seats_sha256": sha256(seats_path),
        "config_sha256": sha256(config_path),
        "result": results,
        "elapsed_wall_seconds": elapsed,
        "process_termination": outcome,
        "post_result_exit_code": proc.returncode,
        "all_ten_logs_started": all(item["started"] for item in log_checks),
        "all_ten_logs_completed": all(item["completed"] for item in log_checks),
        "basic_errors": [item["slot"] for item in log_checks if item["basic_error"]],
        "player_status": status,
        "seat_log_checks": log_checks,
        "replay": replay_metadata(replay_path),
    }
    (out / "evaluation.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--arm", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    rec = run_match(args.binary, args.source, args.out, args.arm, args.timeout)
    print(json.dumps({
        "arm": rec["arm"],
        "result": rec["result"],
        "elapsed_wall_seconds": rec["elapsed_wall_seconds"],
        "all_ten_logs_started": rec["all_ten_logs_started"],
        "all_ten_logs_completed": rec["all_ten_logs_completed"],
        "basic_errors": rec["basic_errors"],
        "player_status_exit_codes": [p.get("exit_code") for p in rec["player_status"].get("players", [])],
        "replay": {k: rec["replay"][k] for k in ("size_bytes", "sha256", "format_from_magic", "magic_hex", "ascii_strings_in_prefix")},
        "evaluation_file": str((args.out / "evaluation.json").resolve()),
    }, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
