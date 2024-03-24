import asyncio
import logging
import unittest
from unittest.mock import ANY

import aiohttp
from yarl import URL

from example.server import ExampleServer
from tests.debug_mode import set_debug_mode

log = logging.getLogger()


class Test(unittest.IsolatedAsyncioTestCase):
    def test_ctor(self):
        ExampleServer()

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
                    async with session.get(
                        URL.build(host=s.host, port=s.port, path="/api/test")
                    ) as resp:
                        assert resp.status == 200
                        assert (await resp.text()) == "{}"

                        assert resp.headers == {
                            "Content-Length": ANY,
                            "content-security-policy": "default-src 'self'",
                            "Content-Type": ANY,
                            "Date": ANY,
                            "referrer-policy": "strict-origin-when-cross-origin",
                            "Server": ANY,
                            "x-content-type-options": "nosniff",
                            "x-frame-options": "SAMEORIGIN",
                        }
                s.shutdown_event.set()

    async def test_custom_sec_headers(self):
        s = ExampleServer()
        async with asyncio.timeout(30):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(s.run_app(log))
                await asyncio.sleep(1)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        URL.build(
                            host=s.host, port=s.port, path="/api/custom-sec-headers"
                        )
                    ) as resp:
                        assert resp.status == 200
                        assert (await resp.text()) == "{}"

                        assert resp.headers == {
                            "Content-Length": ANY,
                            "content-security-policy": "foo",
                            "Content-Type": ANY,
                            "Date": ANY,
                            "referrer-policy": "origin",
                            "Server": ANY,
                            "x-content-type-options": "bar",
                            "x-frame-options": "waz",
                        }
                s.shutdown_event.set()

    async def test_bad_api(self):
        s = ExampleServer()
        async with asyncio.timeout(30):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(s.run_app(log))
                await asyncio.sleep(1)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        URL.build(host=s.host, port=s.port, path="/api/fail")
                    ) as resp:
                        assert resp.status == 500
                        assert (await resp.json()) == {
                            "error": "Unhandled Exception",
                            "request_id": ANY,
                        }
                        assert resp.headers == {
                            "Content-Length": ANY,
                            "content-security-policy": "default-src 'self'",
                            "Content-Type": ANY,
                            "Date": ANY,
                            "referrer-policy": "strict-origin-when-cross-origin",
                            "Server": ANY,
                            "x-content-type-options": "nosniff",
                            "x-frame-options": "SAMEORIGIN",
                        }
                s.shutdown_event.set()

    async def test_400(self):
        s = ExampleServer()
        async with asyncio.timeout(30):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(s.run_app(log))
                await asyncio.sleep(1)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        URL.build(host=s.host, port=s.port, path="/api/400")
                    ) as resp:
                        assert resp.status == 400
                        assert (await resp.text()) == "400: Bad Request"
                s.shutdown_event.set()

    async def test_debug_on_off(self):
        s = ExampleServer()
        async with asyncio.timeout(30):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(s.run_app(log))
                await asyncio.sleep(1)
                async with aiohttp.ClientSession() as session:
                    async with set_debug_mode(True):
                        async with session.get(
                            URL.build(host=s.host, port=s.port, path="/api/fail")
                        ) as resp:
                            assert resp.status == 500
                            assert (await resp.json()) == {
                                "error": "Unhandled Exception",
                                "request_id": ANY,
                            }
                    async with set_debug_mode(False):
                        async with session.get(
                            URL.build(host=s.host, port=s.port, path="/api/fail")
                        ) as resp:
                            assert resp.status == 500
                            assert (await resp.json()) == {
                                "error": "Unhandled Exception",
                                "request_id": ANY,
                            }
                s.shutdown_event.set()

    async def test_empty_middlewares(self):
        s = ExampleServer(middlewares=[])
        async with asyncio.TaskGroup() as tg:
            tg.create_task(s.run_app(log))
            await asyncio.sleep(1)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    URL.build(host=s.host, port=s.port, path="/api/fail")
                ) as resp:
                    assert resp.status == 500
                    assert (await resp.text()).startswith("500 Internal Server Error")
            s.shutdown_event.set()

    async def test_get_file(self):
        s = ExampleServer()
        async with asyncio.timeout(30):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(s.run_app(log))
                await asyncio.sleep(1)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        URL.build(host=s.host, port=s.port, path="/api/license")
                    ) as resp:
                        assert resp.status == 200
                        assert (await resp.text()).startswith("MIT License")
                s.shutdown_event.set()
