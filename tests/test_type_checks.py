import logging
from typing import Dict, List, Optional
import unittest
import pydantic
import pytest

from alxhttp.pydantic.basemodel import BaseModel
from alxhttp.pydantic.type_checks import (
  extract_class,
  extract_type_param,
  is_dict,
  is_generic_type,
  is_list,
  is_model_type,
  is_optional,
)

log = logging.getLogger()


class MatchInfo(BaseModel):
  user_id: int


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

  def test_extract_class(self):
    assert extract_class(str) == 'str'
    assert extract_class(MatchInfo) == 'MatchInfo'
    assert extract_class(BaseModel) == 'BaseModel'
    assert extract_class(pydantic.BaseModel) == 'BaseModel'

  def test_extract_type_param(self):
    assert extract_type_param(Optional[str]) == str
    assert extract_type_param(str | None) == str
    assert extract_type_param(List[str]) == str
    assert extract_type_param(List[str | None]) == str | None
    assert extract_type_param(Dict[str, str]) == str
    with pytest.raises(ValueError):
      extract_type_param(str)
