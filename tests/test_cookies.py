import asyncio
from datetime import timedelta
import logging
import unittest
from unittest.mock import Mock

import aiohttp
from yarl import URL


from alxhttp.cookies import RedisHiddenCookie
from alxhttp.json import json_response
from example.server import ExampleServer
import redis.asyncio as redis

log = logging.getLogger()


class TestCookies(unittest.IsolatedAsyncioTestCase):
  async def test_redis_cookie(self):
    c = RedisHiddenCookie('mycookie', timedelta(hours=1))

    async with redis.Redis(host='localhost', port=7379, db=0) as client:
      resp = json_response({})
      await c.set(client, resp, 'topsecret')

      assert resp.cookies['mycookie'].value.startswith('mycookie_')
      assert len(resp.cookies['mycookie'].value) == 73
      assert resp.cookies['mycookie_is_set'].value == '1'

      req = Mock()
      # req.cookies = MagicMock()
      req.cookies.get = Mock(return_value=resp.cookies['mycookie'].value)
      val = await c.get(client, req)
      assert val == 'topsecret'

  async def test_normal_cookies(self):
    s = ExampleServer()
    async with asyncio.timeout(30):
      async with asyncio.TaskGroup() as tg:
        tg.create_task(s.run_app(log))
        await asyncio.sleep(1)
        jar = aiohttp.CookieJar(unsafe=True, treat_as_secure_origin=[URL.build(scheme='http', host=s.host, port=s.port)])
        async with aiohttp.ClientSession(cookie_jar=jar) as session:
          async with session.post(URL.build(scheme='http', host=s.host, port=s.port, path='/api/cookies'), data={}) as resp:
            assert resp.status == 200
            assert (await resp.text()) == '{}'

            assert resp.cookies['plaincookie'].value == 'plainvalue'
            assert resp.cookies['hiddencookie'].value == 'hiddenvalue'
            assert resp.cookies['hiddencookie_is_set'].value == '1'

          async with session.get(URL.build(scheme='http', host=s.host, port=s.port, path='/api/cookies')) as resp:
            assert resp.status == 200
            assert await resp.json() == {
              'c1v': 'plainvalue',
              'c2v': 'hiddenvalue',
            }

          async with session.delete(URL.build(scheme='http', host=s.host, port=s.port, path='/api/cookies')) as resp:
            assert resp.status == 200
            assert await resp.json() == {}
        s.shutdown_event.set()
