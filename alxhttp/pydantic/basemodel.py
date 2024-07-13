import json
import typing
from datetime import datetime
from typing import Type, TypeVar, get_type_hints

import asyncpg
import pydantic

from aiohttp.web import HTTPNotFound
from alxhttp.pydantic.type_checks import is_dict, is_list, is_model_type, is_optional


def recursive_json_loads(type, data):
  """
  json loads anything that requires recursive model verification
  """

  # Unwrap optionals
  if is_optional(type):
    targs = typing.get_args(type)
    return recursive_json_loads(targs[0], data)

  if isinstance(data, str) and (is_dict(type) or is_list(type) or is_model_type(type)):
    return recursive_json_loads(type, json.loads(data))

  if isinstance(data, dict):
    assert is_dict(type) or is_model_type(type)

    for k, v in data.items():
      if is_model_type(type):
        t = get_type_hints(type).get(k)
      else:
        assert is_dict(type)
        t = typing.get_args(type)[1]

      # likely a mistake with the model/record that will be caught by pydantic
      if not t:
        continue

      data[k] = recursive_json_loads(t, v)
  elif isinstance(data, list):
    assert is_list(type)
    type = typing.get_args(type)[0]
    data = [recursive_json_loads(type, d) for d in data]

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
      raise HTTPNotFound()
    record_dict = dict(record)
    record_dict = recursive_json_loads(cls, record_dict)
    return cls.model_validate(record_dict)


class Empty(BaseModel):
  pass
