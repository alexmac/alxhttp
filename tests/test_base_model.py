import json
import logging
import unittest
from typing import Dict, List

import pydantic

from alxhttp.pydantic.basemodel import recursive_json_loads

log = logging.getLogger()


class Model(pydantic.BaseModel):
  some_id: str
  some_name: str | None


class ModelTest1(pydantic.BaseModel):
  some_id: str


class ModelTest2(pydantic.BaseModel):
  some_id: str
  foo: Model | None


class ModelTest3(pydantic.BaseModel):
  some_id: str
  foo: List[Model]


class ModelTest4(pydantic.BaseModel):
  some_id: str
  foo: List[Model] | None


class Model5(pydantic.BaseModel):
  some_id: str
  some_name: str


class ModelTest6B(pydantic.BaseModel):
  foo: int


class ModelTest6A(pydantic.BaseModel):
  foo: ModelTest6B


class ModelTest6(pydantic.BaseModel):
  foo: ModelTest6A


class ModelTest7A(pydantic.BaseModel):
  some_id: int


class ModelTest7(pydantic.BaseModel):
  foo: List[ModelTest7A | None]


class ModelTest8(pydantic.BaseModel):
  foo: Dict[str, Model]


class ModelTest9(pydantic.BaseModel):
  foo: ModelTest1 | ModelTest2


class TestBasic(unittest.IsolatedAsyncioTestCase):
  def test_rec_load1(self):
    assert recursive_json_loads(ModelTest1, {}) == {}

  def test_rec_load2(self):
    assert recursive_json_loads(
      ModelTest2,
      {
        'some_id': 'a',
        'foo': json.dumps(
          {
            'some_id': 'a',
            'some_name': 'b',
          }
        ),
      },
    ) == {
      'some_id': 'a',
      'foo': {
        'some_id': 'a',
        'some_name': 'b',
      },
    }

  def test_rec_load3(self):
    assert recursive_json_loads(
      ModelTest3,
      {
        'some_id': 'a',
        'foo': json.dumps(
          [
            {
              'some_id': 'a',
              'some_name': 'b',
            }
          ]
        ),
      },
    ) == {
      'some_id': 'a',
      'foo': [
        {
          'some_id': 'a',
          'some_name': 'b',
        }
      ],
    }

  def test_rec_load4(self):
    assert recursive_json_loads(
      ModelTest4,
      {
        'some_id': 'a',
        'foo': None,
      },
    ) == {
      'some_id': 'a',
      'foo': None,
    }

  def test_rec_load5(self):
    assert recursive_json_loads(
      Model5,
      {'some_id': 'a', 'blah': 'fff'},
    ) == {'some_id': 'a', 'blah': 'fff'}

  def test_rec_load3a(self):
    assert recursive_json_loads(
      ModelTest3,
      {
        'some_id': 'a',
        'foo': [
          json.dumps(
            {
              'some_id': 'a',
              'some_name': 'b',
            }
          )
        ],
      },
    ) == {
      'some_id': 'a',
      'foo': [
        {
          'some_id': 'a',
          'some_name': 'b',
        }
      ],
    }

  def test_rec_load6(self):
    assert recursive_json_loads(
      ModelTest6,
      {'foo': {'foo': json.dumps({'foo': 'a'})}},
    ) == {'foo': {'foo': {'foo': 'a'}}}

  def test_rec_load7(self):
    assert recursive_json_loads(
      ModelTest7,
      {
        'foo': [json.dumps({'some_id': 12}), None, {'some_id': 14}],
      },
    ) == {
      'foo': [
        {
          'some_id': 12,
        },
        None,
        {
          'some_id': 14,
        },
      ],
    }

  def test_rec_load8(self):
    assert recursive_json_loads(
      ModelTest8,
      {
        'foo': {
          'blah': json.dumps({'some_id': 12}),
        }
      },
    ) == {
      'foo': {
        'blah': {'some_id': 12},
      }
    }

  def test_rec_load9(self):
    assert recursive_json_loads(
      ModelTest9,
      {
        'foo': json.dumps(
          {
            'some_id': 42,
          }
        )
      },
    ) == {'foo': {'some_id': 42}}
    assert recursive_json_loads(
      ModelTest9,
      {
        'foo': {
          'some_id': 42,
        }
      },
    ) == {'foo': {'some_id': 42}}
