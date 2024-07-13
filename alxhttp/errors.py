from typing import Optional

from alxhttp.json import json_dumps
from alxhttp.pydantic.basemodel import BaseModel
from aiohttp.web_exceptions import HTTPBadRequest

from alxhttp.req_id import get_request, get_request_id


class ErrorResponse(BaseModel):
  error: str
  status_code: int
  request_id: Optional[str] = None


class JSONHTTPBadRequest(HTTPBadRequest):
  def __init__(self, message: dict):
    request = get_request()
    request_id = get_request_id(request) if request else None

    super().__init__(
      text=json_dumps(
        {
          'error': 'HTTPBadRequest',
          'status_code': 400,
          'request_id': request_id,
        }
        | message
      ),
      content_type='application/json',
    )
