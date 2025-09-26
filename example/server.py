from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Iterable
from datetime import datetime, timedelta
from functools import partial
from typing import Literal, final

from aiohttp import BodyPartReader, MultipartReader
from aiohttp.typedefs import Middleware
from aiohttp.web import HTTPBadRequest, HTTPInsufficientStorage, Request, Response, WebSocketResponse, json_response

from alxhttp.cookies import HiddenCookie, PlainCookie
from alxhttp.errors import HTTPBadRequest as AlxHTTPBadRequest
from alxhttp.file import get_file
from alxhttp.pydantic.basemodel import BaseModel, Empty, ErrorModel
from alxhttp.pydantic.request import Request as ModelReq
from alxhttp.pydantic.response import EmptyResponse
from alxhttp.pydantic.response import Response as ModelResp
from alxhttp.pydantic.route import add_route, route
from alxhttp.pydantic.ws_request import WSRequest
from alxhttp.pydantic.ws_route import add_ws_route, ws_route
from alxhttp.server import Server
from alxhttp.xray import init_xray


async def handler_test_api(s: ExampleServer, req: Request) -> Response:
  s.app.logger.info('test log')
  return json_response({})


async def handler_test_json(s: ExampleServer, req: Request) -> Response:
  d = await req.json()
  return json_response(d)


async def dump_parts(log: logging.Logger, x: MultipartReader | BodyPartReader):
  if isinstance(x, MultipartReader):
    log.info('MultipartReader')
    async for foo in x:
      if foo:
        await dump_parts(log, foo)
  else:
    assert isinstance(x, BodyPartReader)
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
  await c1.set(r, 'plainvalue')
  await c2.set(r, 'hiddenvalue')
  return r


async def handler_del_cookies(s: ExampleServer, req: Request) -> Response:
  r = json_response(
    {},
  )
  await c1.unset(r)
  await c2.unset(r)
  return r


async def handler_get_cookies(s: ExampleServer, req: Request) -> Response:
  return json_response(
    {'c1v': await c1.get(req), 'c2v': await c2.get(req)},
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


async def handler_normal_400(s: ExampleServer, req: Request) -> Response:
  raise AlxHTTPBadRequest({'foo': 42})


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


@final
class ExampleServer(Server):
  def __init__(self, middlewares: Iterable[Middleware] | None = None, logger: logging.Logger | None = None):
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

    self.app.router.add_get(r'/api/nonpydantic400', partial(handler_normal_400, self))


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


type ServerMsgStrings = Literal['test_msg_a'] | Literal['test_msg_b']


class ServerWSMsg(BaseModel):
  type: ServerMsgStrings


class ServerWSMsgA(ServerWSMsg):
  type: Literal['test_msg_a']  # pyright: ignore[reportIncompatibleVariableOverride]
  foo: int


class ServerWSMsgB(ServerWSMsg):
  type: Literal['test_msg_b']  # pyright: ignore[reportIncompatibleVariableOverride]
  bar: datetime


type ServerMsgs = ServerWSMsgA | ServerWSMsgB


type ClientMsgStrings = Literal['test_client_msg_a'] | Literal['test_client_msg_b']


class ClientWSMsg(BaseModel):
  type: ClientMsgStrings


class ClientWSMsgA(ClientWSMsg):
  type: Literal['test_client_msg_a']  # pyright: ignore[reportIncompatibleVariableOverride]
  foo: int


class ClientWSMsgB(ClientWSMsg):
  type: Literal['test_client_msg_b']  # pyright: ignore[reportIncompatibleVariableOverride]
  bar: datetime


type ClientWSMsgs = ClientWSMsgA | ClientWSMsgB


def loads_clientmsg(msg: str) -> ClientWSMsgs:
  d = json.loads(msg)
  if d['type'] == 'test_client_msg_a':
    return ClientWSMsgA.model_validate(d)
  elif d['type'] == 'test_client_msg_b':
    return ClientWSMsgB.model_validate(d)
  else:
    raise ValueError('oops')


@ws_route('/api/ws/test', match_info=Empty, client_msg=ClientWSMsgs, server_msg=ServerMsgs)
async def ws_test(server: ExampleServer, request: WSRequest[ServerMsgs, Empty, Empty]) -> WebSocketResponse:
  await request.prepare_ws()

  await request.send(ServerWSMsgA(type='test_msg_a', foo=42))

  return request._ws


async def main():  # pragma: nocover
  logging.basicConfig(level=logging.INFO)
  log = logging.getLogger()

  await init_xray(service_name='example', log=log)

  s = ExampleServer()

  add_route(s, s.app.router, validated_api)
  add_ws_route(s, s.app.router, ws_test)

  await s.run_app(log, port=8080)


if __name__ == '__main__':  # pragma: nocover
  asyncio.run(main())
