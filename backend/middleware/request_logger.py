from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Response, Request
from starlette.background import BackgroundTask
from api.pex.pex_mongo import PexMongo
from utils.utils import Utils


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response information using PexMongo for analytics and monitoring.
    """

    async def dispatch(self, request: Request, call_next) -> ASGIApp:
        """
        Dispatch method to intercept and log request and response information.

        Args:
        - request (Request): The incoming request.
        - call_next (ASGIApp): The next ASGI application in the chain.

        Returns:
        - ASGIApp: The ASGI application response.
        """

        response = await call_next(request)

        res_body = b""
        async for chunk in response.body_iterator:
            res_body += chunk

        task = BackgroundTask(
            self.update_peer_history,
            request,
            response,
        )

        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task,
        )

    @staticmethod
    async def update_peer_history(request, response):
        """
        Update peer history with request and response information in PexMongo.

        Args:
        - request (Request): The incoming request.
        - response (Response): The outgoing response.
        """

        request_info = Utils.RequestInfo(
            timestamp=datetime.utcnow().isoformat(),
            request_type=request.method,
            endpoint=str(request.url),
            response_code=str(response.status_code),
        )

        # Log the request info with PexMongo
        await PexMongo.update_peer_request_history(
            client_ip=request.client.host, request_info=request_info
        )
