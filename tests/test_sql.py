import asyncio
from contextlib import asynccontextmanager
import logging
import unittest
from unittest.mock import ANY


import aiohttp
from asyncpg import create_pool
import pydantic
from yarl import URL

from alxhttp.pydantic.route import add_route
from example.sqlserver import get_users_for_org, ExampleServer

log = logging.getLogger()


class Foo:
  def __str__(self):
    return 'foo'


class TestModel(pydantic.BaseModel):
  some_id: str


@asynccontextmanager
async def run_server():
  async with (
    asyncio.timeout(30),
    create_pool(
      user='postgres',
      host='127.0.0.1',
      database='postgres',
      password='test',
    ) as pool,
    asyncio.TaskGroup() as tg,
  ):
    yield pool, tg


class TestSQL(unittest.IsolatedAsyncioTestCase):
  async def test_api(self):
    async with run_server() as (pool, tg):
      s = ExampleServer(pool)
      add_route(s, s.app.router, get_users_for_org)
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)

      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/orgs/org_a1b2c3d4e5f6/users')) as resp:
          assert resp.status == 200
          assert await resp.json() == {
            'org_id': 'org_a1b2c3d4e5f6',
            'users': {
              'u_1a2b3c4d5e6f': {
                'user_id': 'u_1a2b3c4d5e6f',
                'created_at': ANY,
                'updated_at': ANY,
                'google': {
                  'sub': 'sub_4d5e6f7a8b9c',
                  'email': 'user1@example.com',
                  'email_verified': True,
                  'hd': 'example.com',
                  'name': 'User One',
                  'picture': 'https://example.com/user1.jpg',
                  'given_name': 'User',
                  'family_name': 'One',
                  'created_at': ANY,
                  'updated_at': ANY,
                },
                'roles': ['owner'],
              },
              'u_2b3c4d5e6f7a': {
                'user_id': 'u_2b3c4d5e6f7a',
                'created_at': ANY,
                'updated_at': ANY,
                'google': {
                  'sub': 'sub_5e6f7a8b9c0d',
                  'email': 'user2@example.com',
                  'email_verified': True,
                  'hd': 'example.com',
                  'name': 'User Two',
                  'picture': 'https://example.com/user2.jpg',
                  'given_name': 'User',
                  'family_name': 'Two',
                  'created_at': ANY,
                  'updated_at': ANY,
                },
                'roles': ['viewer'],
              },
              'u_3c4d5e6f7a8b': {
                'user_id': 'u_3c4d5e6f7a8b',
                'created_at': ANY,
                'updated_at': ANY,
                'google': {
                  'sub': 'sub_6f7a8b9c0d1e',
                  'email': 'user3@example.com',
                  'email_verified': True,
                  'hd': 'example.com',
                  'name': 'User Three',
                  'picture': 'https://example.com/user3.jpg',
                  'given_name': 'User',
                  'family_name': 'Three',
                  'created_at': ANY,
                  'updated_at': ANY,
                },
                'roles': ['viewer'],
              },
            },
          }

      s.shutdown_event.set()
