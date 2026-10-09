"""Run beside Hermes using only the existing Softmax agent HTTP protocol.

Chat: coach lines arrive through `wait`, go to the Hermes run API unchanged, and the reply goes back through `say`.
Research: when the optimizer profile is installed, coach tasks become inbound messages in the harness's `comms/inbox`,
and every message the harness writes to `comms/outbox` is said in the chat once. The two folders are the only place the
bridge and the research harness meet (ide-mvp autoresearch runtime design, Oct 6, §comms).
"""

import asyncio
import fcntl
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast
from uuid import uuid4

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

# A coach line that stops the run in progress instead of becoming the next prompt.
STOP = "/stop"
# The harness's research modes; a task whose `area` is one of them asks for that mode.
ResearchMode = Literal["investigation", "scouting", "experimentation", "maintenance", "planning"]
MODES = {"investigation", "scouting", "experimentation", "maintenance", "planning"}
# `say` refuses longer text (observatory-api MAX_SAY_CHARS); longer replies go as consecutive lines.
MAX_SAY = 20_000


class Config(BaseModel):
    player_id: str
    agent: str
    softmax_url: str
    hermes_url: str
    player_token: SecretStr
    service_key: SecretStr
    session_id: str
    # Absent under the gateway plugin, where the runtime's configured model and provider apply.
    model: str | None = None
    provider: str | None = None
    # Set when the backend installed this bridge; it reports in with it so the backend can mark the instance ready.
    bundle_id: str | None = None
    # The autoresearch workspace (`AUTORESEARCH_WORKSPACE`) once the optimizer profile is installed; absent, there is
    # no harness to relay to and the bridge is chat only. The compose template always writes the key, empty when unset.
    workspace: Path | None = None

    @field_validator("workspace", mode="before")
    @classmethod
    def empty_is_none(cls, value: object) -> object:
        return None if value == "" else value


class Line(BaseModel):
    role: str
    text: str
    images: list[object] = Field(default_factory=list)


class Identity(BaseModel):
    subject_type: str
    subject_id: str


class Idempotency(BaseModel):
    supported: bool
    durable: bool
    retention_seconds: int = Field(gt=60)


class Features(BaseModel):
    runs_idempotency: Idempotency


class Capabilities(BaseModel):
    features: Features


class Created(BaseModel):
    run_id: str


class Result(Created):
    session_id: str
    status: str
    output: str = ""


class Message(BaseModel):
    seq: int
    line: Line
    visitor: str | None = Field(default=None, alias="from")


class Batch(BaseModel):
    cursor: int
    chat: list[Message]


class Change(BaseModel):
    kind: str
    collection: str | None
    key: str | None
    deleted: bool


class Changes(BaseModel):
    changes: list[Change]
    cursor: int


class Task(BaseModel):
    """A `tasks` record body (observatory-core `bodies.py` `Task`), the fields the relay reads."""

    model_config = ConfigDict(extra="allow")
    text: str
    origin: str
    prediction: str
    doneWhen: str
    status: str
    state: str
    area: str | None = None


class TaskRecord(BaseModel):
    rev: int
    body: Task


class Inbound(BaseModel):
    id: str
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    author: str
    on_behalf_of: Literal["human"] = "human"


class InboundTask(Inbound):
    kind: Literal["task"] = "task"
    title: str
    mode: ResearchMode
    why: str
    refs: list[str] = Field(default_factory=list)
    priority: Literal["P2"] = "P2"


class InboundSteer(Inbound):
    kind: Literal["steer"] = "steer"
    text: str
    urgency: Literal["now"] = "now"


class Outbound(BaseModel):
    """A harness outbox message (system design §7); kind-specific extensions are the harness's."""

    model_config = ConfigDict(extra="allow")
    id: str
    seq: int
    kind: str
    title: str
    body: str
    in_reply_to: str | None = None


class Pending(BaseModel):
    seq: int
    text: str
    key: str
    retry_until: float
    run_id: str | None = None
    reply: str | None = None


class TaskCompletion(BaseModel):
    state: str = "done"
    status: str = "kept"
    outcome: str


class Acknowledgement(BaseModel):
    set: TaskCompletion
    base_rev: int
    message: str = "Research acknowledged this task"
    idempotency_key: str


class State(BaseModel):
    """The bridge's durable state. Three coroutines share it, each writing only its own fields: the reader the
    changes cursor and the forwarded and stopped tasks, the chat worker the chat cursor, batch, pending run and stop
    seq, the outbox watcher the outbox seq and acknowledgement. `save` is synchronous, so a save never interleaves
    with another coroutine's mutation."""

    cursor: int
    # The changes feed read so far; `None` until the first start reads where "now" is.
    changes_cursor: int | None = None
    # The last outbox seq said in the chat.
    outbox_seq: int = 0
    # Inbox message id by task key, for every coach task delivered to the harness.
    forwarded: dict[str, str] = Field(default_factory=dict)
    # Task keys whose cancellation was steered to the harness.
    stopped: list[str] = Field(default_factory=list)
    # The seq of the last `/stop` honored, so one line stops one run.
    stop_seq: int = 0
    batch: Batch | None = None
    pending: Pending | None = None
    # Retain the exact write until its outbox message is published, including an ambiguous PATCH response.
    acknowledgement: Acknowledgement | None = None


class Store:
    def __init__(self, path: Path, state: State):
        self.path = path
        self.state = state

    def save(self) -> None:
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w") as output:
            output.write(self.state.model_dump_json())
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(self.path)
        directory = os.open(self.path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def is_stop(message: Message) -> bool:
    return message.visitor is None and message.line.role == "coach" and message.line.text.strip().lower() == STOP


def is_coach(message: Message) -> bool:
    # Approval answers belong to their requesting agents; visitor messages are not owner instructions.
    return message.visitor is None and message.line.role == "coach"


async def say(player: httpx.AsyncClient, config: Config, text: str, key: str, **line: object) -> None:
    """Publish `text` as one line, or as consecutive lines when it exceeds what one line may hold."""
    pieces = [text[start : start + MAX_SAY] for start in range(0, len(text), MAX_SAY)] or [text]
    for index, piece in enumerate(pieces):
        response = await player.post(
            f"/v2/cogents/{config.player_id}/say",
            json={"text": piece, "idempotency_key": key if index == 0 else f"{key}:{index + 1}", **line},
        )
        response.raise_for_status()


class ResearchCapability(BaseModel):
    agent: str
    available: bool


class ResearchRecord(BaseModel):
    rev: int
    body: ResearchCapability


REPORT_EVERY = 30


async def report(player: httpx.AsyncClient, config: Config, hermes: httpx.AsyncClient) -> None:
    """Tell the backend this bridge is up and whether Hermes answers; its first report makes the instance ready."""
    capabilities = await hermes.get("v1/capabilities")
    response = await player.put(
        f"/v2/cogents/{config.player_id}/hermes/bridge",
        json={"bundle_id": config.bundle_id, "hermes_ok": capabilities.is_success},
    )
    response.raise_for_status()


async def heartbeat(player: httpx.AsyncClient, config: Config, hermes: httpx.AsyncClient) -> None:
    while True:
        await asyncio.sleep(REPORT_EVERY)
        await report(player, config, hermes)


async def advertise_research(player: httpx.AsyncClient, config: Config) -> None:
    """Publish the bridge's configured capability; presence determines whether it is currently usable."""
    url = f"/v2/cogents/{config.player_id}/c/state/research"
    capability = ResearchCapability(agent=config.agent, available=config.workspace is not None)
    response = await player.get(url)
    revision = None
    if response.status_code != 404:
        response.raise_for_status()
        existing = ResearchRecord.model_validate(response.json())
        if existing.body == capability:
            return
        revision = existing.rev
    response = await player.put(
        url, json={"body": capability.model_dump(), "base_rev": revision, "idempotency_key": str(uuid4())}
    )
    response.raise_for_status()


async def presence(player: httpx.AsyncClient, config: Config, busy: bool) -> None:
    response = await player.put(
        f"/v2/cogents/{config.player_id}/presence/agents/{config.agent}",
        json={
            "state": "thinking" if busy else "idle",
            "doing": f"Working on your message ({STOP} interrupts)" if busy else "Waiting for a message",
        },
    )
    response.raise_for_status()


async def stop_requested(store: Store, config: Config, player: httpx.AsyncClient) -> int | None:
    """A coach `/stop` after the message being answered, not yet honored: later in its batch, or after the batch.

    Holds the read open up to five seconds, so a stop is seen as soon as it commits and the run's status is read
    again no later than that."""
    batch = store.state.batch
    assert batch is not None
    response = await player.get(f"/v2/cogents/{config.player_id}/wait", params={"cursor": batch.cursor, "timeout": 5})
    response.raise_for_status()
    later = batch.chat[1:] + Batch.model_validate(response.json()).chat
    return max((m.seq for m in later if is_stop(m) and m.seq > store.state.stop_seq), default=None)


async def turn(store: Store, config: Config, player: httpx.AsyncClient, hermes: httpx.AsyncClient) -> None:
    state = store.state
    batch = state.batch
    assert batch is not None
    # A `/stop` with nothing running, or one already honored, is not a prompt.
    while batch.chat and is_stop(batch.chat[0]):
        batch.chat.pop(0)
        store.save()
    if not batch.chat:
        state.cursor = batch.cursor
        state.batch = None
        store.save()
        return
    message = batch.chat[0]
    if state.pending is None:
        response = await hermes.get("v1/capabilities")
        response.raise_for_status()
        idempotency = Capabilities.model_validate(response.json()).features.runs_idempotency
        if not idempotency.supported or not idempotency.durable:
            raise RuntimeError("Hermes requires durable submission idempotency")
        state.pending = Pending(
            seq=message.seq,
            text=message.line.text,
            key=f"softmax:{config.player_id}:{config.agent}:{message.seq}",
            retry_until=time.time() + min(600, idempotency.retention_seconds - 60),
            reply="Please send a text description; this bridge does not yet forward images."
            if message.line.images
            else None,
        )
        store.save()
    pending = state.pending
    assert pending.seq == message.seq
    await presence(player, config, True)
    if pending.reply is None and pending.run_id is None:
        if time.time() >= pending.retry_until:
            raise RuntimeError("Submission outcome unknown; reconcile before resubmitting")
        response = await hermes.post(
            "v1/runs",
            headers={"Idempotency-Key": pending.key},
            json={
                "input": pending.text,
                "instructions": (
                    f"This IDE session acts as Softmax player {config.player_id}. "
                    f"Its Softmax API server is {config.softmax_url.removesuffix('/observatory')}. "
                    "Use that URL explicitly with --server on softmax and coworld commands; "
                    "their defaults or repository examples may target a different server. "
                    "The player credential is provisioned in the standard Softmax credential store. "
                    "Never print credentials or request them in chat. Resolve game and league IDs "
                    "against this server rather than reusing IDs from another environment."
                ),
                "session_id": config.session_id,
                **config.model_dump(include={"model", "provider"}, exclude_none=True),
            },
        )
        response.raise_for_status()
        pending.run_id = Created.model_validate(response.json()).run_id
        store.save()
    while pending.reply is None:
        response = await hermes.get(f"v1/runs/{pending.run_id}")
        response.raise_for_status()
        result = Result.model_validate(response.json())
        if result.run_id != pending.run_id or result.session_id != config.session_id:
            raise RuntimeError("Hermes run identity mismatch")
        if result.status == "completed":
            pending.reply = result.output or "The agent completed without a text response."
            store.save()
        elif result.status in {"queued", "running", "stopping"}:
            await presence(player, config, True)
            stop_seq = await stop_requested(store, config, player)
            if stop_seq is not None:
                response = await hermes.post(f"v1/runs/{pending.run_id}/stop")
                response.raise_for_status()
                state.stop_seq = stop_seq
                pending.reply = "Stopped at your request."
                store.save()
        elif result.status == "waiting_for_approval":
            response = await hermes.post(f"v1/runs/{pending.run_id}/stop")
            response.raise_for_status()
            await asyncio.sleep(1)
        elif result.status in {"failed", "cancelled", "interrupted"}:
            pending.reply = (
                f"The agent run was {result.status} before completing. "
                "Its work may be incomplete; inspect the result before retrying. "
                "No automatic retry was made."
            )
            store.save()
        else:
            raise RuntimeError(f"Unknown Hermes run status: {result.status}")
    await say(player, config, pending.reply, pending.key)
    batch.chat.pop(0)
    state.pending = None
    store.save()
    print(f"Published reply for message {pending.seq}", flush=True)


def deliver(inbox: Path, message: InboundTask | InboundSteer) -> None:
    """One immutable file per inbound message, written whole; a retry finds the file and leaves it."""
    message_id = message.id
    inbox.mkdir(parents=True, exist_ok=True)
    destination = inbox / f"{message_id}.json"
    if destination.exists():
        return
    temporary = inbox / f".{message_id}.tmp"
    temporary.write_text(message.model_dump_json())
    temporary.replace(destination)


async def forward_tasks(store: Store, config: Config, player: httpx.AsyncClient, changes: list[Change]) -> None:
    """A queued coach task becomes an inbound `task`; cancelling a forwarded one becomes an urgent `steer`."""
    assert config.workspace is not None
    inbox = config.workspace / "comms/inbox"
    state = store.state
    author = f"coach:{config.player_id}"
    for change in changes:
        if change.kind != "record" or change.collection != "tasks" or change.deleted:
            continue
        response = await player.get(f"/v2/cogents/{config.player_id}/c/tasks/{change.key}")
        if response.status_code == 404:
            continue  # deleted since this change was written; its own deletion change follows
        response.raise_for_status()
        task = TaskRecord.model_validate(response.json()).body
        if task.origin != "coach" or task.area not in MODES:
            continue  # the hub's own tasks, and coach tasks that are not research requests, stay with the hub
        assert change.key is not None
        if task.status == "queued" and change.key not in state.forwarded:
            message_id = f"{config.player_id}:task:{change.key}"
            why = "\n\n".join(
                part for part in (task.prediction, task.doneWhen and f"Done when: {task.doneWhen}") if part
            )
            deliver(
                inbox,
                InboundTask(
                    id=message_id,
                    author=author,
                    title=task.text[:500],
                    mode=cast(ResearchMode, task.area),
                    why=why or task.text,
                ),
            )
            state.forwarded[change.key] = message_id
            store.save()
        elif task.status == "cancelled" and change.key in state.forwarded and change.key not in state.stopped:
            deliver(
                inbox,
                InboundSteer(
                    id=f"{config.player_id}:stop:{change.key}",
                    author=author,
                    text=f"Stop task {state.forwarded[change.key]}: {task.text}",
                ),
            )
            state.stopped.append(change.key)
            store.save()


async def acknowledge(store: Store, config: Config, player: httpx.AsyncClient, key: str, message: Outbound) -> None:
    """Close the task `message` answers, against the revision read now; a task the coach already closed stays as it is.

    The write is kept until its message is said, so a lost PATCH response is retried with the same key and body. A
    stale revision means the write never applied: it is rebuilt against the current revision under a new key, since
    the server refuses a reused key with a different write.
    """
    state = store.state
    while True:
        if state.acknowledgement is None:
            response = await player.get(f"/v2/cogents/{config.player_id}/c/tasks/{key}")
            response.raise_for_status()
            record = TaskRecord.model_validate(response.json())
            if record.body.state == "done":
                return
            state.acknowledgement = Acknowledgement(
                set=TaskCompletion(outcome=f"{message.title}\n\n{message.body}"),
                base_rev=record.rev,
                idempotency_key=f"softmax:{config.player_id}:{config.agent}:ack:{message.seq}:{record.rev}",
            )
            store.save()
        response = await player.patch(
            f"/v2/cogents/{config.player_id}/c/tasks/{key}", json=state.acknowledgement.model_dump()
        )
        if response.status_code == 409:
            state.acknowledgement = None
            store.save()
            continue
        response.raise_for_status()
        return


async def relay_outbox(store: Store, config: Config, player: httpx.AsyncClient) -> None:
    """Every harness message is said in the chat once; a note answering a forwarded task also closes that task."""
    assert config.workspace is not None
    outbox = config.workspace / "comms/outbox"
    if not outbox.is_dir():
        return  # the harness has not initialized its workspace yet
    state = store.state
    # Files are `<seq>-<id>.json` (runtime design §comms), so the ones already said are skipped unread.
    messages = sorted(
        (
            Outbound.model_validate_json(path.read_text())
            for path in outbox.glob("*.json")
            if not path.name.startswith(".") and int(path.stem.split("-", 1)[0]) > state.outbox_seq
        ),
        key=lambda item: item.seq,
    )
    for message in messages:
        if message.seq <= state.outbox_seq:
            continue
        key = next((task for task, sent in state.forwarded.items() if sent == message.in_reply_to), None)
        if key is not None and message.kind == "note":
            await acknowledge(store, config, player, key, message)
        await say(
            player,
            config,
            f"{message.title}\n\n{message.body}",
            f"softmax:{config.player_id}:{config.agent}:outbox:{message.seq}",
            aside=f"research {message.kind}",
            **({"goal_id": key} if key is not None else {}),
        )
        state.outbox_seq = message.seq
        state.acknowledgement = None
        store.save()


async def reader(store: Store, config: Config, player: httpx.AsyncClient) -> None:
    """Hold the changes feed open and forward coach research tasks to the harness as they commit."""
    assert config.workspace is not None
    while True:
        state = store.state
        response = await player.get(
            f"/v2/cogents/{config.player_id}/changes", params={"cursor": state.changes_cursor, "wait": 25}
        )
        response.raise_for_status()
        changes = Changes.model_validate(response.json())
        await forward_tasks(store, config, player, changes.changes)
        state.changes_cursor = changes.cursor
        store.save()


async def chat_worker(store: Store, config: Config, player: httpx.AsyncClient, hermes: httpx.AsyncClient) -> None:
    """Answer coach lines one Hermes run at a time; `wait` holds the read open until a line arrives."""
    while True:
        state = store.state
        if state.batch is None:
            await presence(player, config, False)
            response = await player.get(
                f"/v2/cogents/{config.player_id}/wait", params={"cursor": state.cursor, "timeout": 25}
            )
            response.raise_for_status()
            state.batch = Batch.model_validate(response.json())
            state.batch.chat = [message for message in state.batch.chat if is_coach(message)]
            store.save()
        await turn(store, config, player, hermes)


async def outbox_watcher(store: Store, config: Config, player: httpx.AsyncClient) -> None:
    """Say harness messages within half a second of their arrival; files already said are skipped by name."""
    while True:
        await relay_outbox(store, config, player)
        await asyncio.sleep(0.5)


async def run(directory: Path, *, ready: asyncio.Event | None = None) -> None:
    """``ready`` is set once the bridge has checked in; the gateway plugin waits on it before reporting connected."""
    config = Config.model_validate_json((directory / "config.json").read_text())
    async with (
        httpx.AsyncClient(
            base_url=config.softmax_url,
            headers={
                "Authorization": f"Bearer {config.player_token.get_secret_value()}",
                "X-Cogent-Agent": config.agent,
            },
            timeout=35,
        ) as player,
        httpx.AsyncClient(
            base_url=config.hermes_url,
            headers={"Authorization": f"Bearer {config.service_key.get_secret_value()}"},
            timeout=60,
        ) as hermes,
    ):
        response = await player.get("/whoami")
        response.raise_for_status()
        identity = Identity.model_validate(response.json())
        if identity.subject_type != "player" or identity.subject_id != config.player_id:
            raise RuntimeError("Use this player's dedicated agent credential")
        await advertise_research(player, config)
        path = directory / "state.json"
        if path.exists():
            state = State.model_validate_json(path.read_text())
        else:
            response = await player.get(f"/v2/cogents/{config.player_id}/wait", params={"timeout": 0})
            response.raise_for_status()
            state = State(cursor=Batch.model_validate(response.json()).cursor)
        if state.changes_cursor is None:
            # Start at now: tasks from before the bridge existed are not research requests.
            response = await player.get(f"/v2/cogents/{config.player_id}/changes", params={"cursor": "latest"})
            response.raise_for_status()
            state.changes_cursor = Changes.model_validate(response.json()).cursor
        store = Store(path, state)
        store.save()
        if config.bundle_id is not None:
            await report(player, config, hermes)
        if ready is not None:
            ready.set()
        # One failure ends them all; the supervisor restarts the bridge and the durable state resumes.
        async with asyncio.TaskGroup() as group:
            group.create_task(chat_worker(store, config, player, hermes))
            if config.bundle_id is not None:
                group.create_task(heartbeat(player, config, hermes))
            if config.workspace is not None:
                group.create_task(reader(store, config, player))
                group.create_task(outbox_watcher(store, config, player))


if __name__ == "__main__":
    directory = Path(os.environ["SOFTMAX_BRIDGE_DIRECTORY"])
    with (directory / "lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        asyncio.run(run(directory))
