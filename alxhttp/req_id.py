import random

from aiohttp.web import BaseRequest

__req_id_key = "__req_id_middleware"


def _req_id() -> str:
    r = random.getrandbits(128)
    return f"{r:016x}"


def get_request_id(request: BaseRequest) -> str:
    return request.get(__req_id_key, "")


def set_request_id(request: BaseRequest) -> None:
    request[__req_id_key] = _req_id()
