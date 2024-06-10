import types
import typing


def extract_type_param(t: type) -> type:
  targs = typing.get_args(t)
  if not targs:
    raise ValueError
  return targs[0]


def extract_class(t: type) -> str:
  return str(t).split("'")[1].split('.')[-1]


def is_generic_type(t: type) -> bool:
  return len(typing.get_args(t)) > 0


def is_model_type(t: type) -> bool:
  return type(t).__name__ == 'ModelMetaclass'


def is_optional(t: type) -> bool:
  return typing.get_origin(t) in {typing.Union, types.UnionType} and typing.get_args(t)[1] == types.NoneType


def is_list(t: type) -> bool:
  return t is list or typing.get_origin(t) in {list, typing.List}


def is_dict(t: type) -> bool:
  return t is dict or typing.get_origin(t) in {dict, typing.Dict}
