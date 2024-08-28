import logging
import os
import pathlib
import tempfile
import unittest
from datetime import datetime
from typing import Annotated, Dict, List, Optional

from pydantic import Field

from alxhttp.pydantic.basemodel import BaseModel
from alxhttp.pydantic.route import get_route_details
from alxhttp.typescript.type_index import TypeIndex
from alxhttp.typescript.writer import gen_ts_for_route, run_prettier
from example.sqlserver import create_org, delete_org, get_users_for_org_valid_args

log = logging.getLogger()

UPDATE_SNAPSHOTS = False

prettier_opts = ['--trailing-comma', 'es5']


class WithDefaultsAndAnnotations(BaseModel):
  foo: str = 'hello'
  val: str = Field(default='world')
  blah: Annotated[str, 'someconst']
  fff: Annotated[str, BaseModel]


class Opt(BaseModel):
  key: str
  val: str | None


class User(BaseModel):
  user_id: str
  name: str | None
  roles: List[str]
  options: Dict[str, Opt]
  maybe_options: Dict[str, Opt] | None
  deep_opts: Dict[str, Dict[str, Dict[str, Dict[str, Opt]]]]
  opt_union: Optional[str | int]


class Org(BaseModel):
  org_id: str
  created_at: datetime
  users: List[User]
  maybe_users: Optional[List[User]]


cur_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


def _snapshot_typeindex(ti: TypeIndex, out):
  for v in ti.py_to_ts.values():
    out.write(str(v))
  for wf in ti.py_to_wire_func.values():
    out.write(wf + '\n')
  for wf in ti.serialize_wire_func.values():
    out.write(wf + '\n')
  out.flush()


def update_snapshot(ti: TypeIndex, path: pathlib.Path):
  with tempfile.NamedTemporaryFile('r+', suffix='.ts') as f:
    _snapshot_typeindex(ti, f)
    f.flush()
    f.seek(0)
    run_prettier(pathlib.Path(f.name), should_raise=True, opts=prettier_opts)
    new_snapshot = f.read()

  with open(path, mode='w') as f:
    f.write(new_snapshot)


def snapshot_compare(ti: TypeIndex, path: pathlib.Path):
  if UPDATE_SNAPSHOTS:
    update_snapshot(ti, path)

  with tempfile.NamedTemporaryFile('r+', suffix='.ts') as f:
    _snapshot_typeindex(ti, f)
    f.flush()
    f.seek(0)
    run_prettier(pathlib.Path(f.name), should_raise=True, opts=prettier_opts)
    test = f.read()

  with open(path, mode='r') as f:
    actual = f.read()

  assert actual == test


class TestTS(unittest.IsolatedAsyncioTestCase):
  async def test_ts_types(self):
    snapshot = cur_dir / 'test_ts.snapshot.ts'
    ti = TypeIndex()
    for t in [WithDefaultsAndAnnotations, Opt, User, Org]:
      ti.recurse_model(t, init_from_wire=True, init_to_wire=True)
    snapshot_compare(ti, snapshot)

  async def test_route_wrappers(self):
    routes = [
      get_users_for_org_valid_args,
      create_org,
      delete_org,
    ]
    rds = [get_route_details(route) for route in routes]
    for rd in rds:
      gen_ts_for_route(rd, base_path='tests/snapshots', pretty=True)
