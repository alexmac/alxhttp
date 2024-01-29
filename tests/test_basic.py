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

    async def test_unknown_endpoint(self):
        s = ExampleServer()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    URL.build(host=s.host, port=s.port, path="/api/unknown")
            ) as resp:
                assert resp.status == 404
        s.shutdown_event.set()

    async def test_post_request(self):
        s = ExampleServer()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    URL.build(host=s.host, port=s.port, path="/api/test"),
                    data={"key": "value"}
            ) as resp:
                assert resp.status == 200
                assert (await resp.json()) == {"response": "Data received"}
        s.shutdown_event.set()

    async def test_server_timeout(self):
        s = ExampleServer()
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0.01)) as session:
            try:
                await session.get(
                        URL.build(host=s.host, port=s.port, path="/api/slow")
                )
                assert False, "Expected a timeout exception"
            except asyncio.TimeoutError:
                pass # Expected
        s.shutdown_event.set()

    async def test_internal_server_error(self):
        s = ExampleServer()
        # Mocking an internal server function to raise an exception
        with unittest.mock.patch("example.server.internal_function_that_fails", side_effect=Exception):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        URL.build(host=s.host, port=s.port, path="/api/test")
                ) as resp:
                    assert resp.status == 500
        s.shutdown_event.set()

    # Additional test methods can be added below following the same pattern
    # Make sure to clean up by setting 'shutdown_event' at the end of every test

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
