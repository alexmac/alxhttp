import inspect
import os
import time
from pathlib import Path
from typing import List, Type

import asyncpg
import pglast
from typing_extensions import TypeVar

from alxhttp.file_watcher import register_file_listener
from alxhttp.pydantic.basemodel import BaseModel


def get_caller_dir(idx: int = 1) -> Path:
  current_frame = inspect.currentframe()
  caller_frame = inspect.getouterframes(current_frame, 2)
  return Path(os.path.dirname(os.path.abspath(caller_frame[idx].filename)))


ListType = TypeVar('ListType')


class SQLValidator[T: BaseModel]:
  def __init__(self, file: str | Path, cls: Type[T]):
    self.file = get_caller_dir(2) / file
    self._query = None
    if modified_recently(self.file):
      self.validate()
    self.cls = cls
    register_file_listener(self.file, self.validate)

  def __str__(self):
    return self.query

  @property
  def query(self):
    if not self._query:
      self.validate()

    return self._query

  def validate(self) -> None:
    self._query = validate_sql(self.file)

  async def fetchrow(self, conn: asyncpg.pool.PoolConnectionProxy, *args) -> T:
    record = await conn.fetchrow(self.query, *args)
    return self.cls.from_record(record)

  async def fetch(self, conn: asyncpg.pool.PoolConnectionProxy, *args) -> List[T]:
    records = await conn.fetch(self.query, *args)
    return [self.cls.from_record(record) for record in records]

  async def fetchlist[TT](self, list_type: Type[TT], conn: asyncpg.pool.PoolConnectionProxy, *args) -> List[TT]:
    records = await conn.fetch(self.query, *args)
    return [list_type(record[0]) for record in records]  # type: ignore

  async def execute(self, conn: asyncpg.pool.PoolConnectionProxy, *args) -> str:
    return await conn.execute(self.query, *args)


def modified_recently(path: Path) -> bool:
  current_time = time.time()
  modification_time = os.path.getmtime(path)
  return (current_time - modification_time) <= 600


def validate_sql(sql_file: Path) -> str:
  with open(sql_file) as f:
    txt = f.read()

  try:
    pglast.parser.parse_sql(txt)
    print(f'validated {sql_file}')
    return txt
  except Exception as e:
    raise ValueError(f'Unable to parse {sql_file}') from e
