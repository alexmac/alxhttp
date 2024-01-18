import asyncio
import sys
import traceback

from aiohttp.typedefs import Handler
from aiohttp.web import Request, json_response, middleware, HTTPException

from alxhttp.req_id import get_request_id, set_request_id


@middleware
async def unhandled_error_handler(request: Request, handler: Handler):
    try:
        return await handler(request)
    except HTTPException:
        raise
    except Exception as e:
        exc = sys.exception()
        request.app.logger.error(
            {
                "request_id": get_request_id(request),
                "message": "Unhandled Exception",
                "error": {"kind": e.__class__.__name__},
                "stack": repr(traceback.format_tb(exc.__traceback__)) if exc else "",
            }
        )

        # Be nice when debugging and dump the exception pretty-printed to the console
        loop = asyncio.get_running_loop()
        if loop.get_debug():
            request.app.logger.exception("Unhandled Exception")

        return json_response(
            {
                "error": "Unhandled Exception",
                "request_id": get_request_id(request),
            },
            status=500,
        )


@middleware
async def assign_req_id(request: Request, handler: Handler):
    set_request_id(request)
    return await handler(request)
