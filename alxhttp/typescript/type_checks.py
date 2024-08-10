import types
import typing

from alxhttp.typescript.types import SAFE_PRIMITIVE_TYPES, SAFE_PRIMITIVE_TYPES_OR_NONE

TypeType = type | types.UnionType | typing.Annotated


def extract_type_param(t: TypeType) -> type:
  targs = typing.get_args(t)
  if not targs:
    raise ValueError
  return targs[0]


def extract_class(t: TypeType) -> str:
  return str(t).split("'")[1].split('.')[-1]


def is_generic_type(t: TypeType) -> bool:
  return len(typing.get_args(t)) > 0


def is_model_type(t: TypeType) -> bool:
  return type(t).__name__ == 'ModelMetaclass'


def is_union(t: TypeType) -> bool:
  return typing.get_origin(t) in {typing.Union, types.UnionType}


def is_optional(t: TypeType) -> bool:
  return is_union(t) and typing.get_args(t)[1] == types.NoneType and len(typing.get_args(t)) == 2


def is_annotated(t: TypeType) -> bool:
  return typing.get_origin(t) in {typing.Annotated}


def is_type_or_annotated_type(t: TypeType, ta: TypeType):
  return t == ta or (is_annotated(t) and typing.get_args(t)[0] == ta)


def is_literal(t: TypeType) -> bool:
  return typing.get_origin(t) in {typing.Literal}


def get_literal(t: TypeType) -> str | int:
  assert is_literal(t)
  return typing.get_args(t)[0]


def is_list(t: TypeType) -> bool:
  return t is list or typing.get_origin(t) in {list, typing.List}


def is_dict(t: TypeType) -> bool:
  return t is dict or typing.get_origin(t) in {dict, typing.Dict}


def is_union_with_none(t: TypeType) -> bool:
  # This is a more general version of is_optional
  return typing.get_origin(t) in {typing.Union, types.UnionType} and any([x == types.NoneType for x in typing.get_args(t)])


def is_union_of_models(t: TypeType) -> bool:
  return is_union(t) and all([is_model_type(x) for x in typing.get_args(t)])


def is_safe_primitive_type_or_union(t: TypeType) -> bool:
  if is_union_of_safe_primitive_types(t):
    return True
  return t in SAFE_PRIMITIVE_TYPES


def is_union_of_safe_primitive_types(t: TypeType) -> bool:
  if is_union(t):
    return all([x in SAFE_PRIMITIVE_TYPES for x in typing.get_args(t)])
  return False


def is_union_of_safe_primitive_types_or_none(t: TypeType) -> bool:
  if is_union(t):
    return all([x in SAFE_PRIMITIVE_TYPES_OR_NONE for x in typing.get_args(t)])
  return False
