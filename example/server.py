from __future__ import annotations

import asyncio
import logging
from functools import partial
from typing import List, Optional

from aiohttp import BodyPartReader, MultipartReader
from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPBadRequest, Request, Response, json_response
from alxhttp.file import get_file
from alxhttp.xray import init_xray
from alxhttp.server import Server


async def handler_test_api(s: ExampleServer, req: Request) -> Response:
  s.app.logger.info('test log')
  return json_response({})


async def handler_test_json(s: ExampleServer, req: Request) -> Response:
  d = await req.json()
  return json_response(d)


async def dump_parts(log, x: MultipartReader | BodyPartReader):
  if isinstance(x, MultipartReader):
    log.info('MultipartReader')
    async for foo in x:
      await dump_parts(log, foo)
  elif isinstance(x, BodyPartReader):
    log.info('BodyPartReader')
    async for bar in x:
      log.info(bar)


async def handler_test_multipart(s: ExampleServer, req: Request) -> Response:
  log = logging.getLogger()
  x = await req.multipart()
  await dump_parts(log, x)
  return json_response({})


async def handler_test_custom_sec_headers(s: ExampleServer, req: Request) -> Response:
  return json_response(
    {},
    headers={
      'referrer-policy': 'origin',
      'content-security-policy': 'foo',
      'x-content-type-options': 'bar',
      'x-frame-options': 'waz',
    },
  )


async def handler_test_fail(s: ExampleServer, req: Request) -> Response:
  raise ValueError('uh oh')


class CustomHTTPBadRequest(HTTPBadRequest):
  """Here to test a class that avoids the auto-jsonification"""

  pass


async def handler_test_400(s: ExampleServer, req: Request) -> Response:
  raise CustomHTTPBadRequest()


class ExampleServer(Server):
  def __init__(
    self, middlewares: Optional[List[Middleware]] = None, logger: Optional[logging.Logger] = None
  ):
    super().__init__(middlewares=middlewares, logger=logger)

    self.app.router.add_get(r'/api/test', partial(handler_test_api, self))

    self.app.router.add_get(r'/api/json', partial(handler_test_json, self))

    self.app.router.add_post(r'/api/multipart', partial(handler_test_multipart, self))

    self.app.router.add_get(
      r'/api/custom-sec-headers', partial(handler_test_custom_sec_headers, self)
    )

    self.app.router.add_get(r'/api/fail', partial(handler_test_fail, self))

    self.app.router.add_get(r'/api/400', partial(handler_test_400, self))

    self.app.router.add_get(r'/api/license', get_file('LICENSE'))


async def main():  # pragma: nocover
  logging.basicConfig(level=logging.INFO)
  log = logging.getLogger()

  await init_xray(service_name='example', log=log)

  s = ExampleServer()
  await s.run_app(log, port=8080)


if __name__ == '__main__':  # pragma: nocover
  asyncio.run(main())
