"""Hermes gateway entry point bundled in the optimizer profile distribution.

Hermes owns connection, cancellation, and reconnect. No subprocess or detached event loop is started.
"""

import asyncio
import importlib
import json
import logging
import os
from pathlib import Path
from typing import Any


def register(ctx: Any) -> None:
    # These modules are supplied by the host gateway, not by the operator-side package.
    base = importlib.import_module("gateway.platforms.base")
    gateway_config = importlib.import_module("gateway.config")
    bridge = importlib.import_module(".bridge", __package__)
    extras = importlib.import_module("pm.extras")

    def ensure_requirements() -> bool:
        extras.ensure_import("messaging")
        return extras.available("messaging")

    class SoftmaxAdapter(base.BasePlatformAdapter):
        def __init__(self, config: Any) -> None:
            super().__init__(config, gateway_config.Platform("softmax"))
            self.directory = importlib.import_module("hermes_cli.config").get_hermes_home() / "softmax-bridge"
            self.worker: asyncio.Task[None] | None = None
            self.failure: asyncio.Task[None] | None = None

        async def connect(self, *, is_reconnect: bool = False) -> bool:
            # Acquired by the gateway's supported scoped-lock lifecycle; disconnect releases it.
            if not self._acquire_platform_lock("softmax", str(self.directory), "Softmax coach chat"):
                return False
            connected = False
            try:
                config_path = self.directory / "config.json"
                config_path.chmod(0o600)
                binding = bridge.Config.model_validate_json(config_path.read_text())
                credentials = Path.home() / ".softmax" / "credentials.yaml"
                credentials.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                with open(credentials, "w", opener=lambda path, flags: os.open(path, flags, 0o600)) as output:
                    json.dump(
                        {
                            "tokens": {
                                binding.softmax_url.removesuffix(
                                    "/observatory"
                                ): binding.player_token.get_secret_value()
                            }
                        },
                        output,
                    )
                credentials.chmod(0o600)
                ready = asyncio.Event()
                self.worker = asyncio.create_task(bridge.run(self.directory, ready=ready), name="softmax-bridge")
                self.ready_wait = asyncio.create_task(ready.wait())
                done, _ = await asyncio.wait((self.worker, self.ready_wait), return_when=asyncio.FIRST_COMPLETED)
                if self.worker in done:
                    self.worker.result()
                    raise RuntimeError("Softmax bridge stopped before connecting")
                self._mark_connected()
                self.worker.add_done_callback(self._completed)
                connected = True
            finally:
                if not connected:
                    await self.disconnect()
            return True

        def _completed(self, task: asyncio.Task[None]) -> None:
            if task.cancelled():
                return
            error = task.exception()
            if error is not None:
                logging.getLogger(__name__).error(
                    "Softmax bridge stopped", exc_info=(type(error), error, error.__traceback__)
                )
            self._set_fatal_error(
                "softmax_bridge_failed",
                type(error).__name__ if error else "Softmax bridge stopped",
                retryable=True,
            )
            # The gateway's fatal handler owns reconnect scheduling. Keep a reference until disconnect.
            self.failure = asyncio.create_task(self._notify_fatal_error(), name="softmax-bridge-failure")

        async def disconnect(self) -> None:
            if self.worker is not None:
                self.worker.remove_done_callback(self._completed)
                self.worker.cancel()
                self.ready_wait.cancel()
                await asyncio.gather(self.worker, self.ready_wait, return_exceptions=True)
                self.worker = None
            if self.failure is not None and self.failure is not asyncio.current_task():
                self.failure.cancel()
                await asyncio.gather(self.failure, return_exceptions=True)
                self.failure = None
            self._release_platform_lock()
            self._mark_disconnected()

        async def get_chat_info(self, chat_id: str) -> dict[str, str]:
            return {"name": chat_id, "type": "group"}

        async def send(
            self, chat_id: str, content: str, reply_to: str | None = None, metadata: dict[str, Any] | None = None
        ) -> Any:
            # Replies use the bridge's persisted idempotency ledger, never an untracked gateway send.
            return base.SendResult(success=False, error="Use the Softmax bridge reply ledger")

    ctx.register_platform(
        name="softmax",
        label="Softmax",
        adapter_factory=SoftmaxAdapter,
        check_fn=lambda: extras.available("messaging"),
        ensure_deps_fn=ensure_requirements,
        validate_config=lambda config: (
            importlib.import_module("hermes_cli.config").get_hermes_home() / "softmax-bridge" / "config.json"
        ).is_file(),
    )
