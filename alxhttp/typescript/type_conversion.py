import types
import typing
from datetime import datetime

from alxhttp.typescript.type_checks import extract_class, get_literal, is_annotated, is_dict, is_list, is_literal, is_model_type, is_union
from alxhttp.typescript.types import SAFE_PRIMITIVE_TYPES, TSEnum, TSRaw, TSUndefined


def pytype_to_tstype(t: type) -> str:
  if t is str:
    return 'string'
  elif t is bool:
    return 'boolean'
  elif t is int or t is float:
    return 'number'
  elif t is datetime:
    return 'Date'
  elif t is types.NoneType:
    return 'null'
  elif t is TSUndefined:
    return 'undefined'
  elif is_literal(t):
    literal_value = get_literal(t)
    if isinstance(literal_value, str):
      return f"'{literal_value}'"
    return str(literal_value)
  elif is_annotated(t):
    targs = typing.get_args(t)
    if targs[0] in SAFE_PRIMITIVE_TYPES:
      if isinstance(targs[1], TSRaw):
        if isinstance(targs[1].value, str):
          return f"'{targs[1].value}'"
        else:
          return str(targs[1].value)
      elif isinstance(targs[1], TSEnum):
        return f'{targs[1].name}.{targs[1].value}'
      else:
        return pytype_to_tstype(targs[0])
    else:
      return pytype_to_tstype(targs[0])
  elif is_union(t):
    targs = typing.get_args(t)
    return ' | '.join(sorted([pytype_to_tstype(targ) for targ in targs]))
  elif is_list(t):
    return f'[{pytype_to_tstype(typing.get_args(t)[0])}]'
  elif is_dict(t):
    k_type, v_type = typing.get_args(t)
    return f'Record<{pytype_to_tstype(k_type)}, {pytype_to_tstype(v_type)}>'
  elif is_model_type(t):
    return extract_class(t)
  else:
    raise ValueError
