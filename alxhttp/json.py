import json
from datetime import datetime
from typing import Dict, Any
import pydantic
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound


def json_default(x: Any) -> Any:
  if isinstance(x, datetime):
    return x.timestamp()
  elif isinstance(x, pydantic.BaseModel):
    return x.model_dump(mode='json')
  return str(x)


def json_response(x) -> web.Response:
  if isinstance(x, pydantic.BaseModel):
    t = x.model_dump_json()
  else:
    t = json.dumps(x, indent=0, sort_keys=True, default=json_default)
  return web.json_response(text=t)


class JSONHTTPNotFound(HTTPNotFound):
  message = '{}'


class JSONHTTPBadRequest(HTTPBadRequest):
  def __init__(self, message: Dict):
    super().__init__(text=json.dumps(message), content_type='application/json')
