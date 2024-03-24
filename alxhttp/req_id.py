import contextvars
import random

import aiohttp
from aiohttp.web import BaseRequest

__req_id_key = "__req_id_middleware"
__trace_id_key = "__req_id_middleware_trace_id"

current_request = contextvars.ContextVar("current_request")

try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    xray_recorder = None
    pass


def _req_id() -> str:
    r = random.getrandbits(128)
    return f"{r:016x}"


def get_request() -> BaseRequest:
    req: BaseRequest = current_request.get()
    return req


def get_request_id(request: BaseRequest) -> str:
    return request.get(__req_id_key, "")


def get_trace_id(request: BaseRequest) -> str:
    return request.get(__trace_id_key, "")


def set_request_id(request: BaseRequest) -> None:
    trace_id = None
    if xray_recorder is not None:
        try:
            trace = xray_recorder.get_trace_entity()
            if trace and trace.trace_id:
                trace_id = trace.trace_id
        except Exception:
            pass

    request[__req_id_key] = _req_id()
    request[__trace_id_key] = trace_id
