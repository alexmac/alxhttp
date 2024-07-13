from typing import Dict, List, Optional, Tuple
from aiohttp.typedefs import Handler
from aiohttp.web import Request, middleware, StreamResponse
import pydantic
from aiohttp.web_exceptions import HTTPBadRequest

from alxhttp.errors import ErrorResponse
from alxhttp.pydantic.basemodel import BaseModel
from alxhttp.req_id import get_request, get_request_id


class PydanticErrorDetails(BaseModel):
  type: str
  loc: List[int | str]
  msg: str
  input: str
  ctx: Optional[Dict[str, str]] = None


class PydanticErrorResponse(ErrorResponse):
  error: str = pydantic.Field(default='PydanticValidationError')
  errors: List[PydanticErrorDetails]


def fix_loc_list(loc: Tuple[int | str, ...]) -> List[int | str]:
  return [x if isinstance(x, int) or isinstance(x, str) else str(x) for x in loc]


@middleware
async def pydantic_validation(request: Request, handler: Handler) -> StreamResponse:
  """
  Ensure that any Pydantic validation exceptions become JSON
  responses.
  """
  try:
    return await handler(request)
  except pydantic.ValidationError as ve:
    raise PydanticValidationError(
      errors=[PydanticErrorDetails(type=x['type'], loc=fix_loc_list(x['loc']), msg=x['msg'], input=x['input'], ctx=x.get('ctx')) for x in ve.errors(include_url=False)]
    ) from ve


class PydanticValidationError(HTTPBadRequest):
  def __init__(self, errors: List[PydanticErrorDetails]):
    request = get_request()
    request_id = get_request_id(request) if request else None

    super().__init__(
      text=PydanticErrorResponse(status_code=400, request_id=request_id, errors=errors).model_dump_json(),
      content_type='application/json',
    )
