import json
import types
import typing
from datetime import datetime
from typing import Type, TypeVar, get_type_hints

import asyncpg
import pydantic

from alxhttp.json import JSONHTTPNotFound
from alxhttp.pydantic.type_checks import is_dict, is_list, is_model_type


def recursive_json_loads(type, data: dict | list) -> dict | list:
  """
  json loads anything that requires recursive model verification
  """
  if isinstance(data, dict):
    for k, v in data.items():
      if isinstance(v, str):
        t = get_type_hints(type)[k]

        # Unwrap optional
        if typing.get_origin(t) == typing.Union:
          targs = typing.get_args(t)
          if targs[1] == types.NoneType:
            t = targs[0]
          else:
            raise ValueError

        if is_list(t) or is_dict(t) or is_model_type(t):
          # We've found something where the real type is a string, but the model
          # type suggests we need to json.loads it
          data[k] = recursive_json_loads(t, json.loads(data[k]))
  elif isinstance(data, list):
    if type is not str and len(data) > 1 and isinstance(data[0], str):
      data = [recursive_json_loads(type, json.loads(d)) for d in data]
  return data


BaseModelType = TypeVar('BaseModelType', bound='BaseModel')


class BaseModel(pydantic.BaseModel):
  """
  A Pydantic model with some opinions:
  - extra values are not allowed
  - datetimes are serialized as float timestamps
  """

  model_config = pydantic.ConfigDict(extra='forbid', json_encoders={datetime: lambda v: v.timestamp()})

  @classmethod
  def from_record(cls: Type[BaseModelType], record: asyncpg.Record | None) -> BaseModelType:
    if not record:
      raise JSONHTTPNotFound()
    record_dict = dict(record)
    record_dict = recursive_json_loads(cls, record_dict)
    return cls.model_validate(record_dict)


class Empty(BaseModel):
  pass
