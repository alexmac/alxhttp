import asyncio
from contextlib import asynccontextmanager
import logging
import unittest
from unittest.mock import ANY


import aiohttp
from asyncpg import create_pool
import pytest
from yarl import URL

from alxhttp.pydantic.basemodel import Empty
from alxhttp.pydantic.route import add_route
from alxhttp.middleware.defaults import default_middleware
from alxhttp.sql import SQLValidator
from example.sqlserver import get_org, get_org_invalid, get_users_for_org, ExampleServer, get_users_for_org_list

log = logging.getLogger()


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
  async def test_sql_validator_missing(self):
    with pytest.raises(ValueError):
      SQLValidator('does_not_exist.sql', Empty)

  async def test_sql_validator_invalid(self):
    with pytest.raises(ValueError) as e:
      SQLValidator('test_sql.invalid_sql.sql', Empty)
    assert e.value.args[0].startswith('Unable to parse')

  async def test_sql_validator_valid(self):
    s = SQLValidator('test_sql.valid_sql.sql', Empty)
    s.validate()
    assert s.query == 'select\n  *\nfrom\n  sometable;'
    assert str(s) == 'select\n  *\nfrom\n  sometable;'

  async def test_api_orgs_users(self):
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

  async def test_api_orgs_users_list(self):
    async with run_server() as (pool, tg):
      s = ExampleServer(pool)
      add_route(s, s.app.router, get_users_for_org_list)
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)

      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/orgs/org_a1b2c3d4e5f6/users/list')) as resp:
          assert resp.status == 200
          assert await resp.json() == {
            'org_id': 'org_a1b2c3d4e5f6',
            'users': [
              {
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
              {
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
              {
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
            ],
          }

      s.shutdown_event.set()

  async def test_api_orgs(self):
    async with run_server() as (pool, tg):
      s = ExampleServer(pool)
      add_route(s, s.app.router, get_org)
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)

      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/orgs/org_a1b2c3d4e5f6')) as resp:
          assert resp.status == 200
          assert await resp.json() == {
            'org_id': 'org_a1b2c3d4e5f6',
            'org_name': 'Organization One',
            'created_at': ANY,
            'updated_at': ANY,
          }

      s.shutdown_event.set()

  async def test_api_orgs_invalid(self):
    async with run_server() as (pool, tg):
      s = ExampleServer(pool, middlewares=default_middleware())
      add_route(s, s.app.router, get_org_invalid)
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)

      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/orgs/org_a1b2c3d4e5f6/invalid')) as resp:
          assert resp.status == 400
          assert await resp.json() == {
            'errors': [
              {
                'input': 'Organization One',
                'loc': [
                  'org_name',
                ],
                'msg': 'Extra inputs are not permitted',
                'type': 'extra_forbidden',
              },
            ],
          }

      s.shutdown_event.set()

  async def test_api_orgs_missing(self):
    async with run_server() as (pool, tg):
      s = ExampleServer(pool, middlewares=default_middleware())
      add_route(s, s.app.router, get_org_invalid)
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)

      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/orgs/org_b1b2c3d4e5f8/invalid')) as resp:
          assert resp.status == 404

      s.shutdown_event.set()
