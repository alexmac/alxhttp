import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def set_debug_mode(debug: bool = True):
    loop = asyncio.get_running_loop()
    old_debug_value = loop.get_debug()
    try:
        loop.set_debug(debug)
        yield
    finally:
        loop.set_debug(old_debug_value)
