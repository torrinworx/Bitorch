import json
from datetime import datetime

from starlette.types import ASGIApp
from fastapi import Response, Request
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware

from utils import Peer
from api.pex import PexMongo

# TODO: Sanatize request info before logging to db


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response information using PexMongo for analytics and monitoring of peers
    on the network making requests.
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

        body_bytes = await request.body()  # read the body here

        # You can access the request body here
        req_body = body_bytes.decode('utf-8')
        # If the body is JSON, you can convert it to a dict
        try:
            req_body = json.loads(req_body)
        except json.JSONDecodeError:
            # The body is not JSON, handle according to your application's needs
            req_body = None

        # Create a new request with the same scope and the original body
        # so that other parts of the application can still access the body
        request = Request(request.scope, receive=request._receive)

        response = await call_next(request)

        res_body = b""
        async for chunk in response.body_iterator:
            res_body += chunk

        task = BackgroundTask(
            self.update_peer_history,
            request,
            response,
            req_body,
            res_body
        )

        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=task,
        )

    @staticmethod
    async def update_peer_history(request, response, req_body, res_body):
        """
        Update peer history and _last_seen with request and response information in PexMongo.

        Args:
        - request (Request): The incoming request.
        - response (Response): The outgoing response.
        """
        # TODO: Ensure this is logging the incoming request regardless of a response. if the request is rejected then it should be logged as such and for what reason.

        # Collect query params
        # NOTE: Ensure that we are not logging api keys or sensitive info that doesn't carry the expectation of privacy
        query_params = (
            request.query_params._dict if hasattr(request, "query_params") else {}
        )

        # Collect form data if it's a form request
        form_data = await request.form() if hasattr(request, "form") else None
        if form_data:
            form_data = dict(form_data)  # Convert from MultiDict to dict
            # Assume we do not want to log file content here
            form_data.pop("file", None)  # remove large or sensitive items

        # Selectively log headers
        sanitized_headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ["authorization", "cookie"]
        }

        request_info = Peer.RequestInfo(
            timestamp=datetime.utcnow().isoformat(),
            request_type=request.method,
            endpoint=str(request.url.path),
            query_params=query_params,
            req_body=req_body,
            res_body=res_body,
            headers=sanitized_headers,
            response_code=str(response.status_code),
        )

        # Log the request info with PexMongo
        await PexMongo.update_peer_request_history(
            client_ip=request.client.host, request_info=request_info
        )
