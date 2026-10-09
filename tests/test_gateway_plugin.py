import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from types import SimpleNamespace

import pytest

from plugins import softmax as gateway_plugin
from plugins.softmax.bridge import Config


@pytest.mark.asyncio
@pytest.mark.parametrize("fail", [False, True])
async def test_gateway_owns_bridge_lifetime_and_failure_notification(tmp_path, monkeypatch, fail):
    tmp_path = tmp_path / "softmax-bridge"
    tmp_path.mkdir()
    stop = asyncio.Event()
    closed = asyncio.Event()
    fatal = asyncio.Event()
    config = Config(
        player_id="ply_test",
        agent="hermes",
        session_id="durable-chat",
        softmax_url="http://softmax/api/observatory",
        hermes_url="http://hermes/",
        player_token="cga_scoped",
        service_key="runtime-key",
    ).model_dump()
    config.update(player_token="cga_scoped", service_key="runtime-key")
    (tmp_path / "config.json").write_text(json.dumps(config))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    async def run(directory, *, ready):
        assert directory == tmp_path
        try:
            ready.set()
            await stop.wait()
            raise RuntimeError("transport failed")
        finally:
            closed.set()

    class Adapter(ABC):
        @abstractmethod
        async def disconnect(self) -> None: ...

        @abstractmethod
        async def get_chat_info(self, chat_id: str) -> dict[str, str]: ...

        def __init__(self, config, platform):
            self.connected = False
            self.locked = False

        def _acquire_platform_lock(self, *args):
            self.locked = True
            return True

        def _release_platform_lock(self):
            self.locked = False

        def _mark_connected(self):
            self.connected = True

        def _mark_disconnected(self):
            self.connected = False

        def _set_fatal_error(self, code, message, *, retryable):
            assert code == "softmax_bridge_failed"
            assert message == "RuntimeError"
            assert retryable

        async def _notify_fatal_error(self):
            await self.disconnect()
            fatal.set()

    modules = {
        "gateway.platforms.base": SimpleNamespace(BasePlatformAdapter=Adapter),
        "gateway.config": SimpleNamespace(Platform=str),
        ".bridge": SimpleNamespace(run=run, Config=Config),
        "pm.extras": SimpleNamespace(available=lambda _: True),
        "hermes_cli.config": SimpleNamespace(get_hermes_home=lambda: tmp_path.parent),
    }
    monkeypatch.setattr(gateway_plugin, "importlib", SimpleNamespace(import_module=lambda name, *args: modules[name]))
    registration = {}
    gateway_plugin.register(SimpleNamespace(register_platform=lambda **kwargs: registration.update(kwargs)))
    adapter = registration["adapter_factory"](SimpleNamespace(extra={"directory": str(tmp_path)}))
    assert await adapter.connect()
    assert adapter.connected and adapter.locked
    credential_path = tmp_path / ".softmax" / "credentials.yaml"
    assert credential_path.stat().st_mode & 0o777 == 0o600
    if fail:
        stop.set()
        async with asyncio.timeout(1):
            await fatal.wait()
    else:
        await adapter.disconnect()
    assert closed.is_set()
    assert not adapter.connected and not adapter.locked
    assert adapter.worker is None
