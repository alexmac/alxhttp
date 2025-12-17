import logging
import os
import pathlib
import tempfile
import unittest
from datetime import datetime
from typing import IO, Annotated, Any, ClassVar, Literal, Self

from pydantic import ConfigDict, Field

from alxhttp.pydantic.basemodel import BaseModel
from alxhttp.pydantic.route import get_route_details
from alxhttp.pydantic.ws_route import get_ws_route_details
from alxhttp.typescript.type_index import TypeIndex
from alxhttp.typescript.wrappers.wrappers import shared_defs
from alxhttp.typescript.writer import gen_ts_for_route, gen_ts_for_ws_route, run_prettier
from example.server import ws_test
from example.sqlserver import create_org, create_org_2, delete_org, get_users_for_org_valid_args

log = logging.getLogger()

UPDATE_SNAPSHOTS = False

prettier_opts = ['--trailing-comma', 'es5']


class TestAnnotation:
  pass


class WithDefaultsAndAnnotations(BaseModel):
  foo: str = 'hello'
  val: str = Field(default='world')
  blah: Annotated[str, 'someconst']
  fff: Annotated[str, TestAnnotation]


class Opt(BaseModel):
  key: str
  val: str | None


class User(BaseModel):
  user_id: str
  name: str | None
  nope: None
  roles: list[str]
  options: dict[str, Opt]
  maybe_options: dict[str, Opt] | None
  deep_opts: dict[str, dict[str, dict[str, dict[str, Opt]]]]
  opt_union: str | int | None
  tups: tuple[str, str]
  alts: Literal['foo', 'bar']


class Org(BaseModel):
  org_id: str
  created_at: datetime
  users: list[User]
  maybe_users: list[User] | None


class RecursiveType(BaseModel):
  child: 'RecursiveType|None'


type SomeID = str


class DoubleDict(BaseModel):
  foo: dict[SomeID, dict[str, Any]]


class Mem1(BaseModel):
  service_id: Literal['mem1']
  service_name: str


class Mem2(BaseModel):
  service_id: Literal['mem2']
  foo: str


class Mem3(BaseModel):
  service_id: str
  foo: str


type ServerMsgType = Literal['update_item'] | Literal['delete_item']


class WSMsg(BaseModel):
  type: ServerMsgType
  stream: str | None = None


class CanvasItemUpdate(WSMsg):
  type: Literal['update_item']  # pyright: ignore[reportIncompatibleVariableOverride]
  foo: int


class CanvasItemDelete(WSMsg):
  type: Literal['delete_item']  # pyright: ignore[reportIncompatibleVariableOverride]
  item_id: str


class CanvasItemFixItem(WSMsg):
  model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')
  type: Literal['fix_item']  # pyright: ignore[reportIncompatibleVariableOverride]
  item_id: str


class CanvasItemFoxItem(WSMsg):
  model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid')
  type: Literal['fox_item']  # pyright: ignore[reportIncompatibleVariableOverride]
  item_id: str


class ServerMsg(BaseModel):
  data: CanvasItemUpdate | CanvasItemDelete | CanvasItemFixItem | CanvasItemFoxItem
  ignore_me: ClassVar[str] = 'fff'


class TreeNode(BaseModel):
  foo: str
  children: list[Self]


type ResourceCardData = Mem1 | Mem2 | Mem3

type Blah = Mem1 | Mem2


class Holder(BaseModel):
  data: ResourceCardData
  maybe_data: Blah | None


cur_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


def _snapshot_typeindex(ti: TypeIndex, out: IO[str]):
  out.write(shared_defs())
  for v in ti.py_to_ts.values():
    out.write(str(v))
  for v in ti.py_to_ts_union.values():
    out.write(str(v))
  for wf in ti.py_to_wire_func.values():
    out.write(wf + '\n')
  for wf in ti.serialize_wire_func.values():
    out.write(wf + '\n')
  out.flush()


def update_snapshot(ti: TypeIndex, path: pathlib.Path):
  with tempfile.NamedTemporaryFile('r+', suffix='.ts') as f:
    _snapshot_typeindex(ti, f)  # pyright: ignore[reportArgumentType]
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
    _snapshot_typeindex(ti, f)  # pyright: ignore[reportArgumentType]
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
    for t in [WithDefaultsAndAnnotations, Opt, User, Org, RecursiveType, DoubleDict, Holder, ServerMsg, Blah, ResourceCardData, TreeNode]:
      ti.recurse_model(t, init_from_wire=True, init_to_wire=True)  # pyright: ignore[reportArgumentType]  # ty:ignore[invalid-argument-type]
    snapshot_compare(ti, snapshot)

  async def test_route_wrappers(self):
    routes = [
      get_users_for_org_valid_args,
      create_org,
      delete_org,
      create_org_2,
    ]
    rds = [get_route_details(route) for route in routes]
    for rd in rds:
      gen_ts_for_route(rd, base_path='tests/snapshots', pretty=True)

  async def test_ws_route_wrappers(self):
    routes = [ws_test]
    rds = [get_ws_route_details(route) for route in routes]
    for rd in rds:
      gen_ts_for_ws_route(rd, base_path='tests/snapshots', pretty=True)
