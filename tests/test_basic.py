import asyncio
from datetime import datetime
import json
import logging
import unittest
from unittest.mock import ANY


import aiohttp
import pydantic
from yarl import URL

from alxhttp.json import json_response
from alxhttp.middleware.g_state import g_state
from alxhttp.middleware.defaults import default_middleware
from example.server import ExampleServer
from tests.debug_mode import set_debug_mode

log = logging.getLogger()


class Foo:
  def __str__(self):
    return 'foo'


class ModelTest(pydantic.BaseModel):
  some_id: str


class TestBasic(unittest.IsolatedAsyncioTestCase):
  def test_ctor(self):
    ExampleServer()

  def test_ctor_with_logger(self):
    ExampleServer(logger=log)

  def test_ctor_with_xray_middleware(self):
    default_middleware(include_xray=True)

  def test_json_response(self):
    r = json_response([42])
    assert json.loads(r.text or '') == [42]

    r = json_response([datetime(year=2000, month=1, day=2, microsecond=42)])
    x = json.loads(r.text or '')[0]
    assert str(x).endswith('.000042')

    r = json_response([Foo()])
    assert json.loads(r.text or '') == ['foo']

    x = ModelTest.model_validate({'some_id': 'foo'})

    r = json_response([x])
    assert json.loads(r.text or '') == [{'some_id': 'foo'}]

    r = json_response(x)
    assert json.loads(r.text or '') == {'some_id': 'foo'}

  async def test_cancel(self):
    s = ExampleServer(middlewares=[])
    async with asyncio.TaskGroup() as tg:
      t = tg.create_task(s.run_app(log))
      await asyncio.sleep(1)
      t.cancel()

  async def test_api(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/test')) as resp:
            assert resp.status == 200
            assert (await resp.text()) == '{}'

            assert resp.headers == {
              'Content-Length': ANY,
              'content-security-policy': "default-src 'self'",
              'Content-Type': ANY,
              'Date': ANY,
              'referrer-policy': 'strict-origin-when-cross-origin',
              'Server': ANY,
              'x-content-type-options': 'nosniff',
              'x-frame-options': 'SAMEORIGIN',
            }
        s.shutdown_event.set()

  async def test_g_state(self):
    md = default_middleware()
    md.append(g_state)
    s = ExampleServer(middlewares=md)
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/test')) as resp:
            assert resp.status == 200
            assert (await resp.text()) == '{}'
            assert dict(resp.cookies['g_state']) == {
              'expires': ANY,
              'path': '/',
              'comment': '',
              'domain': 'localhost',
              'max-age': '0',
              'secure': '',
              'httponly': '',
              'version': '',
              'samesite': '',
            }
        s.shutdown_event.set()

  async def test_custom_sec_headers(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/custom-sec-headers')) as resp:
            assert resp.status == 200
            assert (await resp.text()) == '{}'

            assert resp.headers == {
              'Content-Length': ANY,
              'content-security-policy': 'foo',
              'Content-Type': ANY,
              'Date': ANY,
              'referrer-policy': 'origin',
              'Server': ANY,
              'x-content-type-options': 'bar',
              'x-frame-options': 'waz',
            }
        s.shutdown_event.set()

  async def test_bad_api(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/fail')) as resp:
            assert resp.status == 500
            assert (await resp.json()) == {
              'error': 'Unhandled Exception',
              'request_id': ANY,
            }
            assert resp.headers == {
              'Content-Length': ANY,
              'content-security-policy': "default-src 'self'",
              'Content-Type': ANY,
              'Date': ANY,
              'referrer-policy': 'strict-origin-when-cross-origin',
              'Server': ANY,
              'x-content-type-options': 'nosniff',
              'x-frame-options': 'SAMEORIGIN',
            }
        s.shutdown_event.set()

  async def test_400(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/400')) as resp:
            assert resp.status == 400
            assert (await resp.text()) == '400: Bad Request'
        s.shutdown_event.set()

  async def test_debug_on_off(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with set_debug_mode(True):
            async with session.get(URL.build(host=s.host, port=s.port, path='/api/fail')) as resp:
              assert resp.status == 500
              assert (await resp.json()) == {
                'error': 'Unhandled Exception',
                'request_id': ANY,
              }
          async with set_debug_mode(False):
            async with session.get(URL.build(host=s.host, port=s.port, path='/api/fail')) as resp:
              assert resp.status == 500
              assert (await resp.json()) == {
                'error': 'Unhandled Exception',
                'request_id': ANY,
              }
        s.shutdown_event.set()

  async def test_empty_middlewares(self):
    s = ExampleServer(middlewares=[])
    async with asyncio.TaskGroup() as tg:
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)
      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/fail')) as resp:
          assert resp.status == 500
          assert (await resp.text()).startswith('500 Internal Server Error')
      s.shutdown_event.set()

  async def test_default_error(self):
    s = ExampleServer()
    async with asyncio.TaskGroup() as tg:
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)
      async with aiohttp.ClientSession() as session:
        async with session.get(URL.build(host=s.host, port=s.port, path='/api/default-aiohttp-error')) as resp:
          assert resp.status == 507
          assert await resp.json() == {
            'error': 'Insufficient Storage',
            'request_id': ANY,
          }

      s.shutdown_event.set()

  async def test_get_file(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
          async with session.get(URL.build(host=s.host, port=s.port, path='/api/license')) as resp:
            assert resp.status == 200
            assert (await resp.text()).startswith('MIT License')
        s.shutdown_event.set()

  async def test_405_is_json(self):
    s = ExampleServer()
    async with asyncio.TaskGroup() as tg:
      tg.create_task(s.run_app(log))
      await asyncio.sleep(1)
      async with aiohttp.ClientSession() as session:
        async with session.post(URL.build(host=s.host, port=s.port, path='/api/license'), data='foo') as resp:
          assert resp.status == 405
          assert await resp.json() == {
            'error': 'Method Not Allowed',
            'request_id': ANY,
          }
      s.shutdown_event.set()
