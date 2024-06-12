import inspect
import os
from pathlib import Path
from typing import Type

import asyncpg
import pglast
from alxhttp.file_watcher import register_file_listener
from alxhttp.pydantic.basemodel import BaseModel


def get_caller_dir(idx: int = 1) -> Path:
  current_frame = inspect.currentframe()
  caller_frame = inspect.getouterframes(current_frame, 2)
  return Path(os.path.dirname(os.path.abspath(caller_frame[idx].filename)))


class SQLValidator[T: BaseModel]:
  def __init__(self, file: str | Path, cls: Type[T]):
    self.file = get_caller_dir(2) / file
    self.query = validate_sql(self.file)
    self.cls = cls
    register_file_listener(self.file, self.validate)

  def __str__(self):
    return self.query

  def validate(self) -> None:
    self.query = validate_sql(self.file)

  async def fetchrow(self, conn: asyncpg.pool.PoolConnectionProxy, *args) -> T:
    record = await conn.fetchrow(self.query, *args)
    return self.cls.from_record(record)


def validate_sql(sql_file: Path) -> str:
  try:
    with open(sql_file) as f:
      txt = f.read()
  except Exception:
    raise ValueError(f'Unable to find/open {sql_file}')

  try:
    pglast.parser.parse_sql(txt)
    return txt
  except Exception:
    raise ValueError(f'Unable to parse {sql_file}')
