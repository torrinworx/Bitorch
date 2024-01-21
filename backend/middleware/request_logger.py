from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> ASGIApp:
        client_host = request.client.host
        print(f"Request from {client_host}")
        response = await call_next(request)
        return response
