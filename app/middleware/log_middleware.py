import time
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.request")

# 不记录日志的健康检查路径
_SKIP_PATHS = {"/", "/docs", "/openapi.json", "/favicon.ico"}


class RequestLogMiddleware(BaseHTTPMiddleware):
    """记录每条 HTTP 请求：方法、路径、状态码、耗时、客户端 IP"""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = (time.monotonic() - start) * 1000

        ip = (request.headers.get("x-forwarded-for") or
              (request.client.host if request.client else "unknown"))

        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            level,
            "[REQUEST] %s %s -> %d  %.1fms  ip=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            ip,
        )
        return response
