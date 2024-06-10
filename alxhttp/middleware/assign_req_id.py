from aiohttp.typedefs import Handler
from aiohttp.web import Request, middleware, StreamResponse

from alxhttp.req_id import set_request_id, current_request


@middleware
async def assign_req_id(request: Request, handler: Handler) -> StreamResponse:
  set_request_id(request)
  token = current_request.set(request)
  try:
    return await handler(request)
  finally:
    current_request.reset(token)
