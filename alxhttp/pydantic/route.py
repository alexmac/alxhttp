from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

from aiohttp import web
import humps

from alxhttp.pydantic.basemodel import Empty
from alxhttp.pydantic.request import BodyType, MatchInfoType, QueryType, Request
from alxhttp.pydantic.response import Response, ResponseType
from alxhttp.server import Server, ServerHandler
from functools import partial

from aiohttp.web_urldispatcher import UrlDispatcher


@dataclass
class RouteDetails:
  name: str
  verb: str
  match_info: Type
  body: Type
  query: Type
  response: Type
  ts_name: str


def get_route_details(func) -> RouteDetails:
  return RouteDetails(
    name=func._alxhttp_route_name,
    verb=func._alxhttp_route_verb,
    match_info=func._alxhttp_match_info,
    response=func._alxhttp_response,
    body=func._alxhttp_body,
    query=func._alxhttp_query,
    ts_name=func._alxhttp_ts_name,
  )


def route(
  verb: str,
  name: str,
  ts_name: str | None = None,
  match_info: Type[MatchInfoType] = Empty,
  body: Type[BodyType] = Empty,
  query: Type[QueryType] = Empty,
  response: Type[ResponseType] = Empty,
):
  def decorator(
    func: Callable[
      [Server, Request[match_info, body, query]],
      Awaitable[Response[response]],
    ],
  ):
    new_ts_name = ts_name
    if not new_ts_name:
      new_ts_name = humps.camelize(func.__name__)

    async def wrapper(
      server: Server, request: web.Request, *args: Any, **kwargs: Any
    ) -> Response[ResponseType]:
      vr = await Request[match_info, body, query].from_request(request)
      return await func(server, vr, *args, **kwargs)

    setattr(wrapper, '_alxhttp_route_name', name)
    setattr(wrapper, '_alxhttp_route_verb', verb)
    setattr(wrapper, '_alxhttp_match_info', match_info)
    setattr(wrapper, '_alxhttp_response', response)
    setattr(wrapper, '_alxhttp_body', body)
    setattr(wrapper, '_alxhttp_query', query)
    setattr(wrapper, '_alxhttp_ts_name', new_ts_name)
    return wrapper

  return decorator


def add_route(server: Server, router: UrlDispatcher, route_handler: ServerHandler) -> None:
  route_details = get_route_details(route_handler)
  handler = partial(route_handler, server)
  router.add_route(route_details.verb, route_details.name, handler)
  print(f'- {route_details.verb} {route_details.name}')
