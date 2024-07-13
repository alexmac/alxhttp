from typing import Dict, List, Optional, Tuple
from aiohttp.typedefs import Handler
from aiohttp.web import Request, middleware, StreamResponse
import pydantic

from alxhttp.pydantic.basemodel import BaseModel, ErrorModel


class PydanticErrorDetails(BaseModel):
  type: str
  loc: List[int | str]
  msg: str
  input: str
  ctx: Optional[Dict[str, str]] = None


class PydanticValidationError(ErrorModel):
  error: str = 'PydanticValidationError'
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
    ).exception() from ve
