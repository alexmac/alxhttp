import asyncio
import json
import logging
import unittest
from unittest.mock import ANY

import aiohttp
import aiohttp.abc
from aiohttp.test_utils import make_mocked_request
from multidict import CIMultiDict


from alxhttp.tests.multipart_bytes_writer import MultipartBytesWriter
from alxhttp.tests.stream_reader import BytesStreamReader, JSONStreamReader
from example.server import (
  ExampleServer,
  handler_test_custom_sec_headers,
  handler_test_json,
  handler_test_multipart,
)

log = logging.getLogger()


class TestMockReqs(unittest.IsolatedAsyncioTestCase):
  async def test_bsr_loop(self):
    BytesStreamReader(data=b'', loop=asyncio.get_running_loop())

  async def test_mock_request(self):
    s = ExampleServer()
    req = make_mocked_request('GET', '/api/test')
    resp = await handler_test_custom_sec_headers(s, req)
    await resp.prepare(req)
    assert resp.status == 200
    assert resp.text == '{}'
    assert resp.headers == CIMultiDict(
      {
        'referrer-policy': 'origin',
        'content-security-policy': 'foo',
        'x-content-type-options': 'bar',
        'x-frame-options': 'waz',
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': '2',
        'Date': ANY,
        'Server': ANY,
      }
    )

  async def test_mock_request_with_json_body(self):
    s = ExampleServer()
    input_data = {'foo': 42}
    req = make_mocked_request(
      'GET',
      '/api/json',
      payload=JSONStreamReader(input_data),
    )
    resp = await handler_test_json(s, req)
    await resp.prepare(req)
    assert resp.status == 200
    assert resp.text == json.dumps(input_data)

  async def test_mock_request_with_multipart_body(self):
    s = ExampleServer()

    with aiohttp.MultipartWriter('mixed', boundary='MYBOUNDARY') as mpwriter:
      mpwriter.append('hello')
      with aiohttp.MultipartWriter('related', boundary='MYBOUNDARY') as subwriter:
        subwriter.append('world')
      mpwriter.append(subwriter)
      mpwriter.append('goodbye')
    content_type, data = await MultipartBytesWriter().get_ct_and_bytes(mpwriter)

    req = make_mocked_request(
      'POST',
      '/api/multipart',
      headers={
        'Content-Type': content_type,
      },
      payload=BytesStreamReader(data),
    )
    resp = await handler_test_multipart(s, req)
    await resp.prepare(req)
    assert resp.status == 200
    assert resp.text == r'{}'
