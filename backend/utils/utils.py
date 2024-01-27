# General and miscelanious utility tools used by any file in the repo

import os
import re
import sys
import json
import socket
from bson import ObjectId
from typing import Optional, List, Dict, Any
from ipaddress import ip_address, IPv4Address, IPv6Address
from pydantic import BaseModel, Field, validator, Extra, root_validator

import httpx
from fastapi.routing import APIRoute
from fastapi import APIRouter


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

        IMPORTANT:

        port and name can be left as "None" only in the scinario that a peer pings and endpoint without sending
        it's Peer clas with an ip/port/name and follows the network standards. Otherwise it's requests to major endpoints
        are ignored.
        """

        ip: str = Field(..., example="127.0.0.1", max_length=45)
        port: Optional[int] = Field(None, gt=1023, lt=65536, example=8080)
        name: Optional[str] = Field(None, max_length=100)

        # Internal fields (NOTE: DO NOT EXPOSE TO PUBLIC ENDPOINTS):
        _last_seen: str = Field(None, extra=Extra.ignore)
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
        _active_tag: bool  # Used to identifiy if the peer has hit the /register endpoint
        _black_listed: bool  # Used to determine if the user has been blacklisted
        _rate_limited: str  # TODO: Maybe some date in the future until not ratelimited? idk how we should do this. Maybe set this value when the peer is rate limited, and the next time it makes a request read this value and compare to current time. Refuse if not current time, and add more time to this value.
        _complies_with_network_standards: bool = Field(default=True)

        @root_validator(pre=True)
        def check_network_standards(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            """
            Validates the Peer instance to check if it complies with network standards.

            Specifically, it checks if both 'port' and 'name' are None. If so, it sets the
            '_complies_with_network_standards' flag to True, indicating that the Peer instance
            is compliant with the network standards where no 'port' and 'name' are required.

            :param values: The dictionary of field values to validate.
            :return: The modified dictionary of field values.
            """
            port, name = values.get("port"), values.get("name")
            values["_complies_with_network_standards"] = port is None and name is None
            return values

        @validator("ip")
        def validate_ip(cls, v: str) -> str:
            """
            Validates the IP address of the Peer.

            In production environments, the IP address must be public and a valid IPv4 or IPv6 address.
            In development environments, this validation is skipped.

            :param v: The IP address to validate.
            :return: The validated IP address.
            :raises ValueError: If the IP address is invalid or private in production environment.
            """
            if Utils.env == "development":
                return v  # Skip validation in development env

            try:
                ip_obj = ip_address(v)
                if not isinstance(ip_obj, (IPv4Address, IPv6Address)):
                    raise ValueError("IP address must be a valid IPv4 or IPv6 address")
                if isinstance(ip_obj, (IPv4Address, IPv6Address)) and ip_obj.is_private:
                    raise ValueError("IP address must be public in production")
            except ValueError as e:
                raise ValueError(f"Invalid IP address format: {e}")
            return v

        @validator("port")
        def validate_port(cls, v: Optional[int]) -> Optional[int]:
            """
            Validates the port number of the Peer.

            The port number must be non-reserved (greater than 1023) and less than 65536.
            If 'None' is provided, it is accepted as a valid value.

            :param v: The port number to validate.
            :return: The validated port number.
            :raises ValueError: If the port number is in the reserved range or invalid.
            """
            if v is not None and (v <= 1023 or v >= 65536):
                raise ValueError("Port number must be between 1024 and 65535")
            return v

        @validator("name")
        def validate_name(cls, v: Optional[str]) -> Optional[str]:
            """
            Validates the name of the Peer.

            The name must consist of alphanumeric characters, spaces, and hyphens only. It should not be empty if provided.

            :param v: The name to validate.
            :return: The validated name.
            :raises ValueError: If the name contains invalid characters or is empty.
            """
            if v is not None:
                v = v.strip()
                if len(v) == 0:
                    raise ValueError("Name cannot be empty")
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
            Throws an error if the data is part of an unknown data structure to prevent internal
            fields from being exposed.
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
                raise TypeError(f"Unsupported data structure: {type(data).__name__}")

    class BitorchAPIRoute(APIRoute):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Add any custom logic here before passing control to the default APIRoute
            # For example, check the request headers, modify the request, etc.

    router = APIRouter(route_class=BitorchAPIRoute)
