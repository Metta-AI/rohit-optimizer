import json
import time

import httpx
import pytest

from plugins.softmax.bridge import Batch, Config, Message, Pending, State, Store, report, turn


@pytest.mark.asyncio
@pytest.mark.parametrize("crash", ["submit", "publish"])
async def test_restarts_reconcile_without_duplicate_run_or_reply(tmp_path, crash):
    config = Config(
        player_id="ply_test",
        agent="hermes",
        softmax_url="http://softmax/api/observatory",
        hermes_url="http://hermes/",
        player_token="cga_test",
        service_key="test",
        session_id="chat",
        model="test",
        provider="test",
    )
    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(
                cursor=2,
                chat=[
                    Message(seq=2, line={"role": "coach", "text": "literal message, no JSON wrapper"}),
                ],
            ),
        ),
    )
    runs = {}
    replies = {}
    interrupted = False

    def serve(request):
        nonlocal interrupted
        path = request.url.path
        if path.endswith("/v1/capabilities"):
            return httpx.Response(
                200,
                json={
                    "features": {
                        "runs_idempotency": {
                            "supported": True,
                            "durable": True,
                            "retention_seconds": 3600,
                        }
                    }
                },
            )
        if path.endswith("/v1/runs"):
            body = json.loads(request.content)
            assert body["input"] == "literal message, no JSON wrapper"
            assert "player ply_test" in body["instructions"]
            assert "API server is http://softmax/api." in body["instructions"]
            assert "--server" in body["instructions"]
            assert "cga_test" not in body["instructions"]
            runs.setdefault(request.headers["Idempotency-Key"], "run1")
            if crash == "submit" and not interrupted:
                interrupted = True
                raise httpx.ReadError("response lost after acceptance")
            return httpx.Response(200, json={"run_id": "run1"})
        if path.endswith("/v1/runs/run1"):
            return httpx.Response(
                200, json={"run_id": "run1", "session_id": "chat", "status": "completed", "output": "plain reply"}
            )
        if path.endswith("/say"):
            body = json.loads(request.content)
            replies.setdefault(body["idempotency_key"], body["text"])
            if crash == "publish" and not interrupted:
                interrupted = True
                raise httpx.ReadError("response lost after publication")
        return httpx.Response(200, json={})

    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        with pytest.raises(httpx.ReadError):
            await turn(store, config, player, hermes)
        recovered = Store(store.path, State.model_validate_json(store.path.read_text()))
        await turn(recovered, config, player, hermes)
        await turn(recovered, config, player, hermes)
    assert len(runs) == len(replies) == 1
    assert recovered.state.cursor == 2
    assert recovered.state.pending is None


@pytest.mark.asyncio
async def test_expired_unknown_submission_is_not_replayed(tmp_path):
    config = Config(
        player_id="ply_test",
        agent="hermes",
        softmax_url="http://softmax",
        hermes_url="http://hermes/",
        player_token="cga_test",
        service_key="test",
        session_id="chat",
        model="test",
        provider="test",
    )
    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(cursor=2, chat=[Message(seq=2, line={"role": "coach", "text": "hello"})]),
            pending=Pending(seq=2, text="hello", key="existing", retry_until=time.time() - 1),
        ),
    )

    def serve(request):
        assert "presence" in request.url.path
        return httpx.Response(200)

    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        with pytest.raises(RuntimeError, match="Submission outcome unknown"):
            await turn(store, config, player, hermes)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["failed", "cancelled", "interrupted", "waiting_for_approval"])
async def test_unsuccessful_run_reports_in_chat_without_resubmitting(tmp_path, monkeypatch, status):
    config = Config(
        player_id="ply_test",
        agent="hermes",
        softmax_url="http://softmax",
        hermes_url="http://hermes/",
        player_token="cga_test",
        service_key="test",
        session_id="chat",
        model="test",
        provider="test",
    )
    store = Store(
        tmp_path / "state.json",
        State(
            cursor=1,
            batch=Batch(cursor=2, chat=[Message(seq=2, line={"role": "coach", "text": "hello"})]),
            pending=Pending(seq=2, text="hello", key="existing", retry_until=0, run_id="run1"),
        ),
    )
    stopped = False
    replies = []

    async def no_sleep(_):
        pass

    monkeypatch.setattr("observatory_hosted_worker.bridge.asyncio.sleep", no_sleep)

    def serve(request):
        nonlocal stopped
        path = request.url.path
        assert path != "/v1/runs", "An unsuccessful run must never be resubmitted automatically"
        if path == "/v1/runs/run1":
            return httpx.Response(
                200,
                json={
                    "run_id": "run1",
                    "session_id": "chat",
                    "status": "cancelled" if stopped else status,
                },
            )
        if path == "/v1/runs/run1/stop":
            assert status == "waiting_for_approval"
            stopped = True
        if path.endswith("/say"):
            replies.append(json.loads(request.content))
        return httpx.Response(200, json={})

    async with (
        httpx.AsyncClient(base_url="http://softmax", transport=httpx.MockTransport(serve)) as player,
        httpx.AsyncClient(base_url="http://hermes", transport=httpx.MockTransport(serve)) as hermes,
    ):
        await turn(store, config, player, hermes)
    assert stopped == (status == "waiting_for_approval")
    assert len(replies) == 1
    assert replies[0]["idempotency_key"] == "existing"
    assert "No automatic retry" in replies[0]["text"]
    assert store.state.pending is None
    assert store.state.batch is not None
    assert store.state.batch.chat == []


@pytest.mark.asyncio
async def test_report_tells_the_backend_whether_hermes_answers():
    config = Config(
        player_id="ply_test",
        agent="hermes-abc",
        softmax_url="http://softmax/api/observatory",
        hermes_url="http://hermes/",
        player_token="cga_test",
        service_key="test",
        session_id="softmax-abc",
        bundle_id="bundle-1",
    )
    reports = []
    hermes_up = True

    def serve(request):
        if request.url.host == "hermes":
            return httpx.Response(200 if hermes_up else 503, json={})
        assert request.method == "PUT"
        assert request.url.path.endswith("/v2/cogents/ply_test/hermes/bridge")
        reports.append(json.loads(request.content))
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(serve)
    async with (
        httpx.AsyncClient(base_url=config.softmax_url, transport=transport) as player,
        httpx.AsyncClient(base_url=config.hermes_url, transport=transport) as hermes,
    ):
        await report(player, config, hermes)
        hermes_up = False
        await report(player, config, hermes)
    assert reports == [
        {"bundle_id": "bundle-1", "hermes_ok": True},
        {"bundle_id": "bundle-1", "hermes_ok": False},
    ]
