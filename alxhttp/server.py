import asyncio
import logging
from typing import List, Optional

from aiohttp import web
from aiohttp.typedefs import Middleware

from alxhttp.logging import JSONAccessLogger
from alxhttp.middleware import default_middleware


class Server:
    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        if middlewares is None:
            middlewares = default_middleware()
        self.app = web.Application(middlewares=middlewares)
        self.host: str
        self.port: int
        self.shutdown_event = asyncio.Event()

    async def setup_ctx(self, app: web.Application):
        """
        Base classes should async-with all their stateful things and yield once.
        When the app shuts down it will return to this generator so they can unwind.
        """
        yield

    async def run_app(
        self, log: logging.Logger, host: str = "localhost", port: int = 0
    ) -> None:
        self.app.cleanup_ctx.append(self.setup_ctx)

        runner = web.AppRunner(self.app, debug=True, access_log_class=JSONAccessLogger)
        await runner.setup()
        site = web.TCPSite(runner, host, port)

        await site.start()

        self.host = host
        self.port = port
        assert isinstance(site._server, asyncio.Server)
        assert len(site._server.sockets) > 0
        s = site._server.sockets[0]
        assert s
        p = s.getsockname()
        assert p
        self.port = p[1]
        log.info({"message": f"listening on {self.host}:{self.port}"})

        try:
            await self.shutdown_event.wait()
        except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
            pass
        finally:
            await runner.cleanup()
