from __future__ import annotations

import asyncio
import logging
from functools import partial
from typing import List, Optional

from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPBadRequest, Request, StreamResponse, json_response

from alxhttp.server import Server


async def test_api(s: ExampleServer, req: Request) -> StreamResponse:
    return json_response({})


async def test_fail(s: ExampleServer, req: Request) -> StreamResponse:
    raise ValueError("uh oh")


async def test_400(s: ExampleServer, req: Request) -> StreamResponse:
    raise HTTPBadRequest()


class ExampleServer(Server):
    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        super().__init__(middlewares=middlewares)

        self.app.router.add_get(r"/api/test", partial(test_api, self))

        self.app.router.add_get(r"/api/fail", partial(test_fail, self))

        self.app.router.add_get(r"/api/400", partial(test_400, self))


async def main():  # pragma: nocover
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    s = ExampleServer()
    await s.run_app(log, port=8080)


if __name__ == "__main__":  # pragma: nocover
    asyncio.run(main())
