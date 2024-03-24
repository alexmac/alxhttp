import asyncio
import sys
import traceback
from typing import List

from aiohttp.typedefs import Handler, Middleware
from aiohttp.web import HTTPException, Request, json_response, middleware
from multidict import CIMultiDict
from alxhttp.headers import content_security_policy

from alxhttp.req_id import get_request_id, set_request_id, current_request

try:
    from aws_xray_sdk.ext.aiohttp.middleware import middleware as xray_middleware
except ImportError:
    xray_middleware = None


def _apply_security_header_defaults(headers: CIMultiDict[str]) -> None:
    if "content-security-policy" not in headers:
        headers["content-security-policy"] = content_security_policy(
            default_src=["self"]
        )
    if "x-content-type-options" not in headers:
        headers["x-content-type-options"] = "nosniff"
    if "x-frame-options" not in headers:
        headers["x-frame-options"] = "SAMEORIGIN"
    if "referrer-policy" not in headers:
        headers["referrer-policy"] = "strict-origin-when-cross-origin"


@middleware
async def default_security_headers(request: Request, handler: Handler):
    try:
        resp = await handler(request)
        _apply_security_header_defaults(resp.headers)
        return resp
    except HTTPException as e:
        _apply_security_header_defaults(e.headers)
        raise

try:
    from aws_xray_sdk.ext.aiohttp.middleware import middleware as xray_middleware
except ImportError:
    xray_middleware = None


def _apply_security_header_defaults(headers: CIMultiDict[str]) -> None:
    if "content-security-policy" not in headers:
        headers["content-security-policy"] = content_security_policy(
            default_src=["self"]
        )
    if "x-content-type-options" not in headers:
        headers["x-content-type-options"] = "nosniff"
    if "x-frame-options" not in headers:
        headers["x-frame-options"] = "SAMEORIGIN"
    if "referrer-policy" not in headers:
        headers["referrer-policy"] = "strict-origin-when-cross-origin"


@middleware
async def default_security_headers(request: Request, handler: Handler):
    try:
        resp = await handler(request)
        _apply_security_header_defaults(resp.headers)
        return resp
    except HTTPException as e:
        _apply_security_header_defaults(e.headers)
        raise


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
    token = current_request.set(request)
    try:
    return await handler(request)
    finally:
        current_request.reset(token)


def default_middleware(include_xray: bool = False) -> List[Middleware]:
    middlewares = [assign_req_id, default_security_headers, unhandled_error_handler]

    if xray_middleware is not None and include_xray:
        middlewares.insert(0, xray_middleware)

    return middlewares
