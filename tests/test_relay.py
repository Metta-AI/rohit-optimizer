import json
import time

import httpx
import pytest

from plugins.softmax.bridge import (
    Batch,
    Change,
    Config,
    Message,
    Pending,
    State,
    Store,
    advertise_research,
    forward_tasks,
    relay_outbox,
    turn,
)


def config(workspace) -> Config:
    return Config(
        player_id="ply_test",
        agent="hermes",
        softmax_url="http://softmax",
        hermes_url="http://hermes/",
        player_token="cga_test",
        service_key="test",
        session_id="chat",
        model="test",
        provider="test",
        workspace=workspace,
    )


def task(status: str, area: str | None = None, state: str = "queued") -> dict:
    return {
        "rev": 3,
        "body": {
            "id": "g-1-abcd",
            "text": "Analyze the final of round 12",
            "origin": "coach",
            "prediction": "",
            "doneWhen": "The replay analysis is in the chat.",
            "status": status,
            "state": state,
            "area": area,
        },
    }


NOTE = {
    "created": "2026-10-07T00:00:00Z",
    "from": "research-agent",
    "iteration": None,
    "refs": [],
    "priority": "P2",
    "id": "m1",
    "seq": 1,
    "kind": "note",
    "title": "Done",
    "body": "x",
    "in_reply_to": "ply_test:task:g-1-abcd",
}


@pytest.mark.asyncio
async def test_coach_tasks_reach_the_inbox_once_and_cancellation_steers(tmp_path):
    records = {
        "g-1-abcd": task("queued", "investigation"),
        "g-2-efgh": {**task("queued"), "body": {**task("queued")["body"], "origin": "player"}},
        "g-3-ijkl": task("queued"),  # a coach task with no research mode is the hub's, not a research request
    }

    def serve(request):
        key = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(200, json=records[key])

    store = Store(tmp_path / "state.json", State(cursor=0, changes_cursor=0))
    changes = [
        Change(kind="record", collection="tasks", key="g-1-abcd", deleted=False),
        Change(kind="record", collection="tasks", key="g-2-efgh", deleted=False),
        Change(kind="record", collection="tasks", key="g-3-ijkl", deleted=False),
        Change(kind="log", collection=None, key=None, deleted=False),
    ]
    inbox = tmp_path / "workspace/comms/inbox"
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await forward_tasks(store, config(tmp_path / "workspace"), player, changes)
        await forward_tasks(store, config(tmp_path / "workspace"), player, changes)  # a replayed change
        files = sorted(inbox.glob("*.json"))
        assert [f.name for f in files] == ["ply_test:task:g-1-abcd.json"]
        sent = json.loads(files[0].read_text())
        assert sent["kind"] == "task" and sent["mode"] == "investigation" and sent["on_behalf_of"] == "human"
        assert sent["title"] == "Analyze the final of round 12" and "Done when" in sent["why"]
        assert store.state.forwarded == {"g-1-abcd": "ply_test:task:g-1-abcd"}

        records["g-1-abcd"] = task("cancelled", "investigation")
        await forward_tasks(store, config(tmp_path / "workspace"), player, changes[:1])
        await forward_tasks(store, config(tmp_path / "workspace"), player, changes[:1])
    steer = json.loads((inbox / "ply_test:stop:g-1-abcd.json").read_text())
    assert steer["kind"] == "steer" and steer["urgency"] == "now" and "ply_test:task:g-1-abcd" in steer["text"]
    assert len(list(inbox.glob("*.json"))) == 2


@pytest.mark.asyncio
async def test_outbox_messages_are_said_once_and_an_acknowledgement_closes_its_task(tmp_path):
    outbox = tmp_path / "workspace/comms/outbox"
    outbox.mkdir(parents=True)
    base = {
        "created": "2026-10-07T00:00:00Z",
        "from": "research-agent",
        "iteration": None,
        "refs": [],
        "priority": "P2",
    }
    (outbox / "0001-m1.json").write_text(
        json.dumps({**base, "id": "m1", "seq": 1, "kind": "highlight", "title": "Surprise", "body": "Scores rose."})
    )
    (outbox / "0002-m2.json").write_text(
        json.dumps(
            {
                **base,
                "id": "m2",
                "seq": 2,
                "kind": "note",
                "title": "Done",
                "body": "Analysis attached.",
                "in_reply_to": "ply_test:task:g-1-abcd",
            }
        )
    )
    said: dict[str, dict] = {}
    patches: list[dict] = []

    def serve(request):
        if request.url.path.endswith("/say"):
            body = json.loads(request.content)
            said.setdefault(body["idempotency_key"], body)
            return httpx.Response(200, json={"seq": len(said)})
        if request.method == "PATCH":
            patches.append(json.loads(request.content))
            return httpx.Response(200, json={})
        return httpx.Response(200, json=task("queued"))

    store = Store(
        tmp_path / "state.json",
        State(cursor=0, changes_cursor=0, forwarded={"g-1-abcd": "ply_test:task:g-1-abcd"}),
    )
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await relay_outbox(store, config(tmp_path / "workspace"), player)
        await relay_outbox(store, config(tmp_path / "workspace"), player)
    assert [body["text"] for body in said.values()] == ["Surprise\n\nScores rose.", "Done\n\nAnalysis attached."]
    assert said["softmax:ply_test:hermes:outbox:2"]["goal_id"] == "g-1-abcd"
    assert "goal_id" not in said["softmax:ply_test:hermes:outbox:1"]
    assert len(patches) == 1 and patches[0]["base_rev"] == 3
    assert patches[0]["set"] == {"state": "done", "status": "kept", "outcome": "Done\n\nAnalysis attached."}
    assert store.state.outbox_seq == 2


@pytest.mark.asyncio
async def test_a_coach_stop_line_stops_the_run_in_progress(tmp_path):
    stopped = []
    polls = 0

    def serve(request):
        nonlocal polls
        path = request.url.path
        if path.endswith("/wait"):
            return httpx.Response(
                200, json={"cursor": 4, "chat": [{"seq": 4, "line": {"role": "coach", "text": " /STOP "}}]}
            )
        if path.endswith("/stop"):
            stopped.append(path)
            return httpx.Response(200, json={})
        if path.endswith("/v1/runs/run1"):
            polls += 1
            return httpx.Response(200, json={"run_id": "run1", "session_id": "chat", "status": "running"})
        return httpx.Response(200, json={})

    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(cursor=2, chat=[Message(seq=2, line={"role": "coach", "text": "long task"})]),
            pending=Pending(seq=2, text="long task", key="k", retry_until=time.time() + 60, run_id="run1"),
        ),
    )
    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        await turn(store, config(None), player, hermes)
    assert stopped == ["/v1/runs/run1/stop"] and polls == 1
    assert store.state.pending is None and store.state.stop_seq == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["http_error", "timeout"])
async def test_failed_stop_is_retried_after_restart(tmp_path, failure):
    attempts = 0
    replies = []

    def serve(request):
        nonlocal attempts
        path = request.url.path
        if path.endswith("/wait"):
            return httpx.Response(
                200, json={"cursor": 4, "chat": [{"seq": 4, "line": {"role": "coach", "text": "/stop"}}]}
            )
        if path.endswith("/stop"):
            attempts += 1
            if attempts == 1:
                if failure == "timeout":
                    raise httpx.ReadTimeout("Stop response timed out", request=request)
                return httpx.Response(503)
            return httpx.Response(200, json={})
        if path.endswith("/v1/runs/run1"):
            return httpx.Response(200, json={"run_id": "run1", "session_id": "chat", "status": "running"})
        if path.endswith("/say"):
            replies.append(json.loads(request.content)["text"])
        return httpx.Response(200, json={})

    path = tmp_path / "state.json"
    store = Store(
        path,
        State(
            cursor=1,
            batch=Batch(cursor=2, chat=[Message(seq=2, line={"role": "coach", "text": "long task"})]),
            pending=Pending(seq=2, text="long task", key="k", retry_until=time.time() + 60, run_id="run1"),
        ),
    )
    store.save()
    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        with pytest.raises(httpx.HTTPError):
            await turn(store, config(None), player, hermes)
        restarted = Store(path, State.model_validate_json(path.read_text()))
        assert restarted.state.stop_seq == 0
        assert restarted.state.pending is not None and restarted.state.pending.reply is None
        assert replies == []
        await turn(restarted, config(None), player, hermes)
    persisted = State.model_validate_json(path.read_text())
    assert attempts == 2
    assert persisted.stop_seq == 4 and persisted.pending is None
    assert replies == ["Stopped at your request."]


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["ack", "say"])
async def test_outbox_acknowledgement_survives_restart(tmp_path, failure):
    outbox = tmp_path / "workspace/comms/outbox"
    outbox.mkdir(parents=True)
    (outbox / "0001-result.json").write_text(
        json.dumps(
            {
                "id": "result",
                "seq": 1,
                "kind": "note",
                "title": "Done",
                "body": "Analysis attached.",
                "in_reply_to": "ply_test:task:g-1-abcd",
            }
        )
    )
    revision = 3
    accepted = {}
    said = {}
    interrupted = False

    def serve(request):
        nonlocal revision, interrupted
        if request.method == "GET":
            return httpx.Response(200, json={**task("queued"), "rev": revision})
        body = json.loads(request.content)
        key = body["idempotency_key"]
        if request.method == "PATCH":
            if key in accepted:
                if accepted[key] != body:
                    return httpx.Response(409, json={"error": "idempotency_key_reused"})
            else:
                assert body["base_rev"] == revision
                accepted[key] = body
                revision += 1
            stage = "ack"
        else:
            assert request.url.path.endswith("/say")
            said.setdefault(key, body)
            stage = "say"
        if stage == failure and not interrupted:
            interrupted = True
            raise httpx.ReadError("Accepted response lost", request=request)
        return httpx.Response(200, json={})

    path = tmp_path / "state.json"
    store = Store(path, State(cursor=0, forwarded={"g-1-abcd": "ply_test:task:g-1-abcd"}))
    store.save()
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        with pytest.raises(httpx.ReadError):
            await relay_outbox(store, config(tmp_path / "workspace"), player)
        recovered = Store(path, State.model_validate_json(path.read_text()))
        await relay_outbox(recovered, config(tmp_path / "workspace"), player)
        await relay_outbox(recovered, config(tmp_path / "workspace"), player)
    assert revision == 4
    assert len(accepted) == len(said) == 1
    assert next(iter(said.values()))["text"] == "Done\n\nAnalysis attached."
    assert State.model_validate_json(path.read_text()).outbox_seq == 1


@pytest.mark.asyncio
async def test_consumed_outbox_files_are_not_parsed(tmp_path):
    outbox = tmp_path / "workspace/comms/outbox"
    outbox.mkdir(parents=True)
    (outbox / "0001-old.json").write_text("not JSON: already consumed")
    (outbox / "0002-new.json").write_text(
        json.dumps({"id": "new", "seq": 2, "kind": "highlight", "title": "New", "body": "result"})
    )
    said = []

    def serve(request):
        said.append(json.loads(request.content))
        return httpx.Response(200, json={})

    store = Store(tmp_path / "state.json", State(cursor=0, outbox_seq=1))
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await relay_outbox(store, config(tmp_path / "workspace"), player)
    assert len(said) == 1 and said[0]["text"] == "New\n\nresult"
    assert store.state.outbox_seq == 2


@pytest.mark.asyncio
async def test_research_capability_is_removed_for_chat_only_restart(tmp_path):
    record = None
    writes = []

    def serve(request):
        nonlocal record
        if request.method == "GET":
            return httpx.Response(404 if record is None else 200, json=record)
        payload = json.loads(request.content)
        assert payload["idempotency_key"]
        assert payload["base_rev"] == (None if record is None else record["rev"])
        writes.append(payload["body"])
        record = {"rev": len(writes), "body": payload["body"]}
        return httpx.Response(200, json=record)

    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await advertise_research(player, config(tmp_path / "workspace"))
        await advertise_research(player, config(tmp_path / "workspace"))
        await advertise_research(player, config(None))
    assert writes == [{"agent": "hermes", "available": True}, {"agent": "hermes", "available": False}]


@pytest.mark.asyncio
async def test_a_stop_in_the_same_batch_as_its_prompt_still_stops(tmp_path):
    stopped = []

    def serve(request):
        path = request.url.path
        if path.endswith("/wait"):
            return httpx.Response(200, json={"cursor": 3, "chat": []})
        if path.endswith("/stop"):
            stopped.append(path)
            return httpx.Response(200, json={})
        if path.endswith("/v1/runs/run1"):
            return httpx.Response(200, json={"run_id": "run1", "session_id": "chat", "status": "running"})
        return httpx.Response(200, json={})

    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(
                cursor=3,
                chat=[
                    Message(seq=2, line={"role": "coach", "text": "long task"}),
                    Message(seq=3, line={"role": "coach", "text": "/stop"}),
                ],
            ),
            pending=Pending(seq=2, text="long task", key="k", retry_until=time.time() + 60, run_id="run1"),
        ),
    )
    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        await turn(store, config(None), player, hermes)
        assert stopped == ["/v1/runs/run1/stop"] and store.state.stop_seq == 3
        assert store.state.batch is not None
        assert [m.seq for m in store.state.batch.chat] == [3]
        await turn(store, config(None), player, hermes)  # the honored stop line is not a prompt
    assert store.state.batch is None and store.state.cursor == 3 and stopped == ["/v1/runs/run1/stop"]


@pytest.mark.asyncio
async def test_a_long_reply_is_said_in_consecutive_lines(tmp_path):
    said = []

    def serve(request):
        if request.url.path.endswith("/say"):
            said.append(json.loads(request.content))
        return httpx.Response(200, json={})

    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(cursor=2, chat=[Message(seq=2, line={"role": "coach", "text": "write a lot"})]),
            pending=Pending(seq=2, text="write a lot", key="k", retry_until=time.time() + 60, reply="x" * 45_000),
        ),
    )
    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        await turn(store, config(None), player, hermes)
    assert [len(line["text"]) for line in said] == [20_000, 20_000, 5_000]
    assert [line["idempotency_key"] for line in said] == ["k", "k:2", "k:3"]


@pytest.mark.asyncio
async def test_a_moved_task_revision_is_acknowledged_against_the_current_one(tmp_path):
    outbox = tmp_path / "workspace/comms/outbox"
    outbox.mkdir(parents=True)
    (outbox / "0001-m1.json").write_text(json.dumps(NOTE))
    revisions = iter([4, 5])  # the coach reordered the queue between the read and the write, once
    patches = []

    def serve(request):
        if request.method == "GET":
            return httpx.Response(200, json={**task("queued", "investigation"), "rev": next(revisions)})
        if request.method == "PATCH":
            patches.append(json.loads(request.content))
            if patches[-1]["base_rev"] != 5:
                return httpx.Response(409, json={"detail": "stale"})
        return httpx.Response(200, json={})

    store = Store(tmp_path / "state.json", State(cursor=0, forwarded={"g-1-abcd": "ply_test:task:g-1-abcd"}))
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await relay_outbox(store, config(tmp_path / "workspace"), player)
    assert [patch["base_rev"] for patch in patches] == [4, 5]
    assert patches[0]["idempotency_key"] != patches[1]["idempotency_key"]
    assert store.state.outbox_seq == 1 and store.state.acknowledgement is None


@pytest.mark.asyncio
async def test_a_task_the_coach_already_closed_is_not_reopened(tmp_path):
    outbox = tmp_path / "workspace/comms/outbox"
    outbox.mkdir(parents=True)
    (outbox / "0001-m1.json").write_text(json.dumps(NOTE))
    methods = []

    def serve(request):
        methods.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, json=task("cancelled", "investigation", state="done"))
        return httpx.Response(200, json={})

    store = Store(tmp_path / "state.json", State(cursor=0, forwarded={"g-1-abcd": "ply_test:task:g-1-abcd"}))
    async with httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player:
        await relay_outbox(store, config(tmp_path / "workspace"), player)
    assert methods == ["GET", "POST"] and store.state.outbox_seq == 1
