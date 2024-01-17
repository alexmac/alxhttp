import logging
from json import dumps
from time import time_ns
from typing import Any

from aiohttp.abc import AbstractAccessLogger
from aiohttp.web import BaseRequest, StreamResponse

from alxhttp.req_id import get_request_id

_compact_separators = (",", ":")


def compact_json(obj: Any) -> str:
    return dumps(
        obj,
        indent=None,
        ensure_ascii=True,
        separators=_compact_separators,
    )


class JSONAccessLogger(AbstractAccessLogger):
    def __init__(self, logger: logging.Logger, log_format: str):
        super().__init__(logger, log_format)

    def log(
        self,
        request: BaseRequest,
        response: StreamResponse,
        time: float,
    ) -> None:
        """
        Taking some naming conventions from:
        https://github.com/opentracing/specification/blob/master/semantic_conventions.md
        """
        self.logger.info(
            compact_json(
                {
                    "message": f"{request.method} {request.url.path} {response.status}",
                    "duration": round(time, 8),
                    "time_ns": time_ns(),
                    "http": {
                        "method": request.method,
                        "status_code": response.status,
                        "url": str(request.url),
                    },
                    "component": "aiohttp",
                    "request_id": get_request_id(request),
                }
            )
        )
