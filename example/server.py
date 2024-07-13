from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from functools import partial
from typing import List, Optional

from aiohttp import BodyPartReader, MultipartReader
from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPBadRequest, Request, Response, json_response, HTTPInsufficientStorage
from alxhttp.cookies import HiddenCookie, PlainCookie
from alxhttp.file import get_file
from alxhttp.pydantic.basemodel import BaseModel, Empty, ErrorModel
from alxhttp.pydantic.request import Request as ModelReq
from alxhttp.pydantic.response import EmptyResponse, Response as ModelResp
from alxhttp.pydantic.route import add_route, route
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


c1 = PlainCookie('plaincookie', timedelta(days=1))
c2 = HiddenCookie('hiddencookie', timedelta(days=1))


async def handler_post_cookies(s: ExampleServer, req: Request) -> Response:
  r = json_response(
    {},
  )
  c1.set(r, 'plainvalue')
  c2.set(r, 'hiddenvalue')
  return r


async def handler_del_cookies(s: ExampleServer, req: Request) -> Response:
  r = json_response(
    {},
  )
  c1.unset(r)
  c2.unset(r)
  return r


async def handler_get_cookies(s: ExampleServer, req: Request) -> Response:
  return json_response(
    {'c1v': c1.get(req), 'c2v': c2.get(req)},
  )


async def handler_test_fail(s: ExampleServer, req: Request) -> Response:
  raise ValueError('uh oh')


async def handler_test_default_error(s: ExampleServer, req: Request) -> Response:
  raise HTTPInsufficientStorage


class CustomHTTPBadRequest(HTTPBadRequest):
  """Here to test a class that avoids the auto-jsonification"""

  pass


async def handler_test_400(s: ExampleServer, req: Request) -> Response:
  raise CustomHTTPBadRequest()


class CustomErrorModel(ErrorModel):
  some_id: str


async def handler_test_custom_error_model(s: ExampleServer, req: Request) -> Response:
  raise CustomErrorModel(some_id='foo').exception()


class CustomSuccessfulModel(BaseModel):
  some_id: str
  something: int


async def handler_test_custom_model(s: ExampleServer, req: Request) -> Response:
  raise CustomSuccessfulModel(some_id='foo', something=42).exception()


class MatchInfo(BaseModel):
  user_id: int


class Body(BaseModel):
  user_name: str


class RespType(MatchInfo, Body):
  pass


class ExampleServer(Server):
  def __init__(self, middlewares: Optional[List[Middleware]] = None, logger: Optional[logging.Logger] = None):
    super().__init__(middlewares=middlewares, logger=logger)

    self.app.router.add_get(r'/api/test', partial(handler_test_api, self))

    self.app.router.add_get(r'/api/json', partial(handler_test_json, self))

    self.app.router.add_get(r'/api/cookies', partial(handler_get_cookies, self))
    self.app.router.add_post(r'/api/cookies', partial(handler_post_cookies, self))
    self.app.router.add_delete(r'/api/cookies', partial(handler_del_cookies, self))

    self.app.router.add_post(r'/api/multipart', partial(handler_test_multipart, self))

    self.app.router.add_get(r'/api/custom-sec-headers', partial(handler_test_custom_sec_headers, self))

    self.app.router.add_get(r'/api/fail', partial(handler_test_fail, self))

    self.app.router.add_get(r'/api/default-aiohttp-error', partial(handler_test_default_error, self))

    self.app.router.add_get(r'/api/400', partial(handler_test_400, self))

    self.app.router.add_get(r'/api/400/custom-model', partial(handler_test_custom_error_model, self))

    self.app.router.add_get(r'/api/200/custom-model', partial(handler_test_custom_model, self))

    self.app.router.add_get(r'/api/license', get_file('LICENSE'))


@route('GET', '/api/empty', ts_name='overrideTsName', match_info=Empty, body=Empty, response=Empty)
async def validated_empty_api(server: ExampleServer, request: ModelReq[Empty, Empty, Empty]) -> EmptyResponse:
  return EmptyResponse()


@route('GET', '/api/users/{user_id}', match_info=MatchInfo, body=Body, response=RespType)
async def validated_api(server: ExampleServer, request: ModelReq[MatchInfo, Body, Empty]) -> ModelResp[RespType]:
  r = RespType.model_validate(
    {
      'user_id': request.match_info.user_id,
      'user_name': request.body.user_name,
    }
  )

  return ModelResp(body=r)


async def main():  # pragma: nocover
  logging.basicConfig(level=logging.INFO)
  log = logging.getLogger()

  await init_xray(service_name='example', log=log)

  s = ExampleServer()

  add_route(s, s.app.router, validated_api)

  await s.run_app(log, port=8080)


if __name__ == '__main__':  # pragma: nocover
  asyncio.run(main())
