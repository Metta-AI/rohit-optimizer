#!/usr/bin/env python3
"""Durable, resource-bounded local operations. Never retries an external write."""
import argparse
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import shutil
import signal
import subprocess
import sys
import time


def save(path, record):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(record, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--key', required=True)
    parser.add_argument('--seconds', type=int, default=120)
    parser.add_argument('--output-mib', type=int, default=8)
    parser.add_argument('--memory-mib', type=int, default=1024)
    parser.add_argument('--file-mib', type=int, default=64)
    parser.add_argument('--reserve-mib', type=int, default=512)
    parser.add_argument('--retry-safe', action='store_true', help='Local reproducible work only; never submission/upload/push')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or not args.key.replace('-', '').replace('_', '').isalnum():
        parser.error('Supply a command and an alphanumeric operation key')
    if min(args.seconds, args.output_mib, args.file_mib, args.memory_mib, args.reserve_mib) <= 0:
        parser.error('Limits must be positive')
    args.state_dir.mkdir(parents=True, exist_ok=True)
    record_path = args.state_dir / (args.key + '.json')
    fingerprint = hashlib.sha256(json.dumps([str(Path.cwd()), command]).encode()).hexdigest()
    with (args.state_dir / (args.key + '.lock')).open('a') as lock:
        # Kernel releases this lock on death. Contention fails instead of launching duplicate work.
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if record_path.exists():
            previous = json.loads(record_path.read_text())
            if previous['fingerprint'] != fingerprint:
                raise ValueError('Operation key already belongs to a different command')
            if previous['status'] == 'completed':
                print(json.dumps(previous))
                return 0
            # A crash around an external write is ambiguous, never proof of failure.
            if not args.retry_safe or previous['attempt'] >= 2:
                print(json.dumps({'status': 'reconciliation_required', 'record': str(record_path)}))
                return 2
        else:
            previous = {'attempt': 0}
        interrupted = False
        def interrupt(signum, frame):
            nonlocal interrupted
            interrupted = True
        signal.signal(signal.SIGTERM, interrupt)
        signal.signal(signal.SIGINT, interrupt)
        record = {'fingerprint': fingerprint, 'status': 'running', 'attempt': previous['attempt'] + 1,
                  'started_at': time.time(), 'output_bytes': 0, 'exit_code': None}
        reserve = args.reserve_mib * 1024 * 1024
        if shutil.disk_usage(args.state_dir).free < reserve:
            record['status'] = 'disk_reserve'
            save(record_path, record)
            print(json.dumps(record))
            return 2
        save(record_path, record)
        output_path = args.state_dir / f'{args.key}.{record["attempt"]}.log'
        # The child sets limits before exec; no shell interpolation and no preexec_fn/thread race.
        child = [sys.executable, str(Path(__file__).resolve()), '_exec', str(args.file_mib), str(args.memory_mib), *command]
        process = subprocess.Popen(child, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + args.seconds
        status = 'completed'
        try:
            with output_path.open('xb') as output:
                while selector.get_map():
                    if interrupted:
                        status = 'interrupted'
                        break
                    if time.monotonic() >= deadline:
                        status = 'timeout'
                        break
                    if shutil.disk_usage(args.state_dir).free < reserve:
                        status = 'disk_reserve'
                        break
                    for key, _ in selector.select(timeout=0.2):
                        data = os.read(key.fd, 65536)
                        if not data:
                            selector.unregister(key.fileobj)
                            continue
                        remaining = args.output_mib * 1024 * 1024 - record['output_bytes']
                        output.write(data[:remaining])
                        record['output_bytes'] += min(len(data), remaining)
                        if len(data) > remaining:
                            status = 'output_limit'
                            break
                    if status != 'completed':
                        break
                if status == 'completed':
                    while process.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.05)
                    if process.poll() is None:
                        status = 'timeout'
        finally:
            # Kill descendants too, including grandchildren holding the output pipe open.
            if process.poll() is None or selector.get_map():
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            selector.close()
            process.stdout.close()
        record.update(status=status if status != 'completed' or process.returncode == 0 else 'failed',
                      exit_code=process.returncode, finished_at=time.time(), output=str(output_path))
        save(record_path, record)
        print(json.dumps(record))
        return 0 if record['status'] == 'completed' else 2


if __name__ == '__main__':
    if sys.argv[1:2] == ['_exec']:
        # Linux kills the directly executed tool if its supervisor is killed, including SIGKILL.
        # Graceful interruption kills the whole process group in the supervisor's finally block.
        if sys.platform == 'linux':
            parent = os.getppid()
            libc = ctypes.CDLL(None, use_errno=True)
            if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
            if os.getppid() != parent or parent == 1:
                raise SystemExit(2)
        cap = int(sys.argv[2]) * 1024 * 1024
        if sys.platform == 'linux':
            memory_cap = int(sys.argv[3]) * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_cap, memory_cap))
        resource.setrlimit(resource.RLIMIT_FSIZE, (cap, cap))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        os.execvp(sys.argv[4], sys.argv[4:])
    raise SystemExit(main())
