# General and miscelanious utility tools used by any file in the repo

import os
import re
import sys
import json
import socket
from bson import ObjectId
from datetime import datetime
from typing import Optional, Callable, List
from pydantic import BaseModel, Field, validator, Extra
from ipaddress import ip_address, IPv4Address, IPv6Address

import httpx
from fastapi.routing import APIRoute
from fastapi import Request, Response, APIRouter
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse


class Utils:
    @staticmethod
    def load_config():
        # Path to the config file
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])), ".", ".config.json"
        )

        # Check if the config file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Read the JSON config file
        with open(config_file, "r") as file:
            config = json.load(file)

        return config

    @staticmethod
    async def get_ip_address():
        # Check the environment
        env = os.getenv("ENV", "development").lower()

        if env == "production":
            # For production, use an external service to get the public IP
            try:
                response = httpx.get("https://api.ipify.org")
                return response.text if response.status_code == 200 else None
            except httpx.HTTPError:
                return None
        else:
            # For development, return the local IP address
            # This is also suitable for Docker containers communicating within the same network
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)

    @staticmethod
    async def get_source_peers():
        # Load the entire configuration
        config_dict = Utils.load_config()

        # Select the appropriate section based on the environment
        section = "production" if Utils.env == "production" else "development"

        # Extract source peers for the specified environment
        if section in config_dict:
            return config_dict[section]
        else:
            raise ValueError(f"Section '{section}' not found in .config.json.")

    @staticmethod
    async def get_my_peer():
        peer_info = {}

        peer_info["ip"] = await Utils.get_ip_address()
        peer_info["port"] = os.getenv("BACKEND_PORT")
        peer_info["name"] = os.getenv("PEER_NAME")

        return peer_info

    env = os.getenv("ENV", "development").lower()
    config = load_config.__func__()

    class JSONEncoder(json.JSONEncoder):
        """Extend json-encoder class"""

        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    class RequestInfo(BaseModel):
        timestamp: str
        request_type: str
        endpoint: str
        response_code: str

    class Peer(BaseModel):
        """
        Represents a peer in a network, encapsulating necessary details such as IP address, port, name, etc.
        This class serves as a critical checkpoint for data validation and security. Given that the data can originate
        from external sources, rigorous validation is applied to each field to ensure integrity and security before
        storage in MongoDB. The class employs strict data type enforcement, pattern matching, and range checking
        to mitigate risks such as injection attacks, data corruption, or unauthorized access attempts.
        """

        ip: str = Field(..., example="127.0.0.1", max_length=45)
        port: int = Field(..., gt=1023, lt=65536, example=8080)
        name: str = Field(..., max_length=100)

        # Internal fields (NOTE: DO NOT EXPOSE TO PUBLIC ENDPOINTS):
        _last_seen: Optional[str] = Field(None, extra=Extra.ignore)
        _request_history: List["Utils.RequestInfo"] = Field(
            [],
            example=[
                {
                    "timestamp": "2024-01-19T12:34:56",
                    "request_type": "GET",
                    "response_code": "200",
                }
            ],
        )

        @validator("ip")
        def validate_ip(cls, v):
            try:
                ip_obj = ip_address(v)
                if Utils.env == "production":
                    if (
                        isinstance(ip_obj, (IPv4Address, IPv6Address))
                        and ip_obj.is_private
                    ):
                        raise ValueError("IP address must be public in production")
                # Always perform general IP format validation
                if not isinstance(ip_obj, (IPv4Address, IPv6Address)):
                    raise ValueError("IP address must be a valid IPv4 or IPv6 address")
            except ValueError:
                raise ValueError("Invalid IP address format")
            return v

        @validator("port")
        def validate_port(cls, v):
            if v <= 1023:
                raise ValueError("Port number must be non-reserved (greater than 1023)")
            return v

        @validator("name")
        def validate_name(cls, v):
            v = v.strip()
            if not re.match(r"^[A-Za-z0-9\s-]+$", v):
                raise ValueError("Name contains invalid characters")
            return v

    class PublicPeerResponse:
        """
        Returns a public-facing representation of the data.

        Example usage in /backend/pex/register.py:

        from utils.utils import Utils

        @router.post(
            "/register",
            tags=["Peer Exchange"],
            summary="Register a new peer",
            description="Accepts peer registration requests and adds them to the peer list.",
        )
        async def register_peer_endpoint(peer: Utils.Peer) -> Dict[str, Any]:
            try:
                added = await PexMongo.add_peer(peer=copy.deepcopy(peer))
                if not added:
                    raise HTTPException(status_code=400, detail="Peer already registered.")

                return {
                    "content": {
                        "peer": Utils.PublicPeerResponse.to_public(peer)
                    },
                    "status_code": 200,
                }
            except Exception as e:
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail=str(e))
        """

        @staticmethod
        def _filter_peer_data(data):
            """
            Filters a single Peer instance to include only public-facing fields.
            """
            public_fields = {"ip", "port", "name"}
            return {field: getattr(data, field) for field in public_fields}

        @staticmethod
        def to_public(data):
            """
            Handles single Peer instances, lists, tuples, sets, nested structures, and dictionaries.
            """
            if isinstance(data, Utils.Peer):
                return Utils.PublicPeerResponse._filter_peer_data(data)
            elif isinstance(data, dict):
                return {
                    key: Utils.PublicPeerResponse.to_public(value)
                    for key, value in data.items()
                }
            elif isinstance(data, (list, tuple, set)):
                return type(data)(
                    Utils.PublicPeerResponse.to_public(item) for item in data
                )
            else:
                return data  # For any other type, return as is

    # NOTE: Attempt at logging request data for rate limitor for each peer:
    class BitorchAPIRoute(APIRoute):
        @staticmethod
        async def log_info(
            request_timestamp,
            client_ip,
            request: Request,
            response: Response,
            req_body,
            res_body,
        ):
            from api.pex.pex_mongo import PexMongo

            # Creating the RequestInfo instance
            request_info = Utils.RequestInfo(
                timestamp=request_timestamp.isoformat(),
                request_type=request.method,
                endpoint=request.url.path,
                response_code=str(response.status_code),
            )

            # Log the request info with PexMongo
            print(
                await PexMongo.update_peer_request_history(
                    client_ip=client_ip, request_info=request_info
                )
            )

        def get_route_handler(self) -> Callable:
            original_route_handler = super().get_route_handler()

            async def custom_route_handler(request: Request) -> Response:
                # Capture the request timestamp at the start of handling the request
                request_timestamp = datetime.utcnow()

                client_ip = request.client.host
                req_body = await request.body()
                response = await original_route_handler(request)

                # Pass the captured timestamp to log_info
                if isinstance(response, StreamingResponse):
                    res_body = b""
                    async for item in response.body_iterator:
                        res_body += item
                    await self.log_info(
                        request_timestamp,
                        client_ip,
                        request,
                        response,
                        req_body,
                        res_body,
                    )
                    return response
                else:
                    res_body = response.body
                    await self.log_info(
                        request_timestamp,
                        client_ip,
                        request,
                        response,
                        req_body,
                        res_body,
                    )
                    return response

            return custom_route_handler

    router = APIRouter(route_class=BitorchAPIRoute)
