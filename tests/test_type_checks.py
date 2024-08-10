import logging
import unittest
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional, Union

import pydantic
import pytest

from alxhttp.pydantic.basemodel import BaseModel
from alxhttp.schemas import prefixed_id
from alxhttp.typescript.type_checks import (
  extract_class,
  extract_type_param,
  get_literal,
  is_annotated,
  is_dict,
  is_generic_type,
  is_list,
  is_literal,
  is_model_type,
  is_optional,
  is_safe_primitive_type_or_union,
  is_type_or_annotated_type,
  is_union_of_safe_primitive_types,
  is_union_of_safe_primitive_types_or_none,
  is_union_with_none,
)

log = logging.getLogger()


class MatchInfo(BaseModel):
  user_id: int


TestID = Annotated[str, prefixed_id('test_')]


class TestTypeChecks(unittest.IsolatedAsyncioTestCase):
  def test_is_list(self):
    assert is_list(list)
    assert is_list(List[str])
    assert not is_list(int)

  def test_is_dict(self):
    assert is_dict(dict)
    assert is_dict(Dict[str, str])
    assert not is_dict(int)

  def test_is_generic_type(self):
    assert is_generic_type(Dict[str, str])
    assert is_generic_type(Optional[str])
    assert is_generic_type(List[str])
    assert is_generic_type(str | None)
    assert not is_generic_type(str)

  def test_is_optional(self):
    assert is_optional(Optional[str])
    assert is_optional(str | None)
    assert not is_optional(List[str])
    assert not is_optional(List[str | None])
    assert not is_optional(Dict[str, str])
    assert not is_optional(str)

  def test_is_model_type(self):
    assert not is_model_type(str)
    assert not is_model_type(Dict[str, str])
    assert is_model_type(MatchInfo)
    assert is_model_type(BaseModel)
    assert is_model_type(pydantic.BaseModel)

  def test_is_annotated(self):
    assert not is_annotated(str)
    assert not is_annotated(Dict[str, str])
    assert is_annotated(TestID)

  def test_is_type_or_annotated_type(self):
    assert not is_type_or_annotated_type(str, int)
    assert is_type_or_annotated_type(str, str)
    assert is_type_or_annotated_type(TestID, str)
    assert not is_type_or_annotated_type(TestID, int)

  def test_is_literal(self):
    assert not is_literal(str)
    assert not is_literal(42)
    assert is_literal(Literal['FOO'])
    assert is_literal(Literal[42])

  def test_get_literal(self):
    assert get_literal(Literal['FOO']) == 'FOO'
    assert get_literal(Literal[42]) == 42

  def test_extract_class(self):
    assert extract_class(str) == 'str'
    assert extract_class(MatchInfo) == 'MatchInfo'
    assert extract_class(BaseModel) == 'BaseModel'
    assert extract_class(pydantic.BaseModel) == 'BaseModel'

  def test_extract_type_param(self):
    assert extract_type_param(Optional[str]) is str
    assert extract_type_param(str | None) is str
    assert extract_type_param(List[str]) is str
    assert extract_type_param(List[str | None]) == str | None
    assert extract_type_param(Dict[str, str]) is str
    with pytest.raises(ValueError):
      extract_type_param(str)
      extract_type_param(str)
    assert extract_class(BaseModel) == 'BaseModel'
    assert extract_class(pydantic.BaseModel) == 'BaseModel'

  def test_is_union_with_none(self):
    assert is_union_with_none(Optional[str])
    assert not is_union_with_none(List[str])
    assert is_union_with_none(str | None)
    assert not is_union_with_none(str | int)

  def test_is_safe_primitive_type_or_union(self):
    assert not is_safe_primitive_type_or_union(Optional[str])  # TODO: should None be a safe primitive type?
    assert is_safe_primitive_type_or_union(str)
    assert is_safe_primitive_type_or_union(str | int)
    assert is_safe_primitive_type_or_union(Union[str, int])
    assert not is_safe_primitive_type_or_union(datetime)

  def test_is_union_of_safe_primitive_types(self):
    assert not is_union_of_safe_primitive_types(Optional[str])  # TODO: should None be a safe primitive type?
    assert not is_union_of_safe_primitive_types(str)
    assert is_union_of_safe_primitive_types(str | int)
    assert is_union_of_safe_primitive_types(Union[str, int])
    assert not is_union_of_safe_primitive_types(datetime)

  def test_is_union_of_safe_primitive_types_or_none(self):
    assert is_union_of_safe_primitive_types_or_none(Optional[str])
    assert not is_union_of_safe_primitive_types_or_none(str)
    assert is_union_of_safe_primitive_types_or_none(str | int)
    assert is_union_of_safe_primitive_types_or_none(Union[str, int])
    assert not is_union_of_safe_primitive_types_or_none(datetime)
