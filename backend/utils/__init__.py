# General and miscelanious utility tools used by any file in the repo

import os
import re
import sys
import json
import socket
from bson import ObjectId
from datetime import datetime
from ipaddress import ip_address, IPv4Address, IPv6Address
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union, Iterable, TypeVar

import httpx
from fastapi import APIRouter
from fastapi.routing import APIRoute


class Utils:
    @staticmethod
    def load_config():
        # Path to the config file
        config_file = os.path.abspath(".config.json")

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
    def get_source_peers() -> List["Peer.Internal"]:
        """
        Retrieves a list of source peers from the configuration file.

        This function reads the list of peers from a specified section based on the environment,
        converts each peer dictionary into a Peer.Internal instance, and returns them as a list.

        Returns:
        - List[Peer.Internal]: A list of Peer.Internal instances representing the source peers.

        Raises:
        - ValueError: If the specified environment section is not found in the configuration.
        """
        # Load the entire configuration
        config_dict = Utils.load_config()

        # Select the appropriate section based on the environment
        section = "production" if Utils.env == "production" else "development"

        # Extract source peers for the specified environment
        if section in config_dict:
            # Convert each dictionary entry into a Peer.Internal instance
            return [Peer.Internal(**peer_data) for peer_data in config_dict[section]]
        else:
            raise ValueError(f"Section '{section}' not found in .config.json.")

    @staticmethod
    async def get_my_peer():
        """
        My peer is treated as an Peer.Public because we don't need to keep track of internal stats
        for our peer.
        """

        peer_info = {
            "ip": await Utils.get_ip_address(),
            "port": os.getenv("BACKEND_PORT"),
            "name": os.getenv("PEER_NAME"),
        }
        return Peer.Public(**peer_info)

    env = os.getenv("ENV", "development").lower()
    config = load_config.__func__()

    class JSONEncoder(json.JSONEncoder):
        """Extend json-encoder class"""

        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    class BitorchAPIRoute(APIRoute):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Add any custom logic here before passing control to the default APIRoute
            # For example, check the request headers, modify the request, etc.

    router = APIRouter(route_class=BitorchAPIRoute)


class Peer:
    class Public(BaseModel):
        """
        Designed to be the public interface with the Peer object. Use cases include:
        - The input parameter for endpoints needing to identify my peer and other peers through peer_list and so on in fastapi endpoints/httpx calls

        IMPORTANT:

        port and name can be left as "None" only in the scinario that a peer pings and endpoint without sending
        it's Peer clas with an ip/port/name and follows the network standards. Otherwise it's requests to major endpoints
        are ignored.
        """

        ip: str = Field(..., example="127.0.0.1", max_length=45)
        port: Optional[int] = Field(None, gt=1023, lt=65536, example=8080)
        name: Optional[str] = Field(None, max_length=100)

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

    class Internal(Public):
        """
        NOTE: For internal use only, meant to be a supper set of Public Peer, including all info from that but hidden and not used
        for defining parameters of a fastapi api endpoint. "Internal" meaning used internally throughout the server in multiple files
        and methods, not meant to be publicly exposed to the peer network.

        Represents a peer in a network, encapsulating necessary details such as IP address, port, name, etc.
        This class serves as a critical checkpoint for data validation and security. Given that the data can originate
        from external sources, rigorous validation is applied to each field to ensure integrity and security before
        storage in MongoDB. The class employs strict data type enforcement, pattern matching, and range checking
        to mitigate risks such as injection attacks, data corruption, or unauthorized access attempts.
        """

        # Internal fields (NOTE: DO NOT EXPOSE TO PUBLIC ENDPOINTS):
        last_seen: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
        request_history: List["Peer.RequestInfo"] = Field(default_factory=list)
        activated: bool = (
            False  # Used to identifiy if the peer has hit our /register endpoint
        )
        registered: bool = (
            False  # Used to identify if we have registered with this peer successfully (continously updated)
        )
        white_listed: bool = (
            False  # Used to allow this peer to have elivated rate limit request privileges (if allowed by user)
        )
        black_listed: bool = False  # Used to determine if the user has been blacklisted
        rate_limited: str = (
            ""  # TODO: Maybe some date in the future until not ratelimited? idk how we should do this. Maybe set this value when the peer is rate limited, and the next time it makes a request read this value and compare to current time. Refuse if not current time, and add more time to this value.
        )
        complies_with_network_standards: bool = Field(default=True)

        @root_validator(pre=True)
        def check_network_standards(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            """
            Validates the Peer instance to check if it complies with network standards.

            Specifically, it checks if both 'port' and 'name' are None. If so, it sets the
            'complies_with_network_standards' flag to True, indicating that the Peer instance
            is compliant with the network standards where no 'port' and 'name' are required.

            :param values: The dictionary of field values to validate.
            :return: The modified dictionary of field values.
            """
            port, name = values.get("port"), values.get("name")
            values["complies_with_network_standards"] = port is None and name is None
            return values

        def to_public(self):
            """
            Creates a Public instance from the Internal instance by
            extracting all fields that are present in the Public definition.
            """
            # Get field names defined in Public
            public_fields = set(
                self.__fields_set__.intersection(Peer.Public.__fields__.keys())
            )
            # Create dict with only the public fields
            public_attrs = {field: getattr(self, field) for field in public_fields}
            # Return a Public instance with those fields
            return Peer.Public(**public_attrs)

    class RequestInfo(BaseModel):
        timestamp: str
        request_type: str
        endpoint: str
        response_code: str
        query_params: Optional[Dict[str, str]] = Field(default=None)
        req_body: Optional[Any] = Field(default=None)
        res_body: Optional[Any] = Field(default=None)
        headers: Optional[Dict[str, str]] = Field(default=None)

    # TODO: Handle validation and sanatization, ensure that we save requests, but disregard malicous params, headers, or form data, and the request.

    T = TypeVar("T", bound=Union[Iterable[Any], Dict[str, Any]])

    @staticmethod
    def to_public(data: Union[T, "Peer.Public", "Peer.Internal"]) -> T:
        """
        Converts Peer.Internal instances to their public representation, and passes
        Peer.Public instances directly. For iterables and dictionaries, it applies conversion recursively.
        """
        if isinstance(data, Peer.Internal):
            return data.to_public()
        elif isinstance(data, Peer.Public):
            # Public instances are returned without modification
            return data
        elif isinstance(data, dict):
            return {key: Peer.to_public(value) for key, value in data.items()}
        elif isinstance(data, (list, tuple, set)):
            public_data_type = type(
                data
            )  # maintain the type of the iterable (list, tuple, set)
            return public_data_type(Peer.to_public(item) for item in data)
        else:
            raise TypeError(f"Unsupported data type: {type(data).__name__}")

    @classmethod
    def to_internal(cls, public_peer: "Peer.Public") -> "Peer.Internal":
        """
        Converts a Public Peer instance to an Internal Peer instance.
        Missing internal attributes will be initialized with their defaults.
        """
        return cls.Internal(**public_peer.dict())


Peer.Internal.update_forward_refs()
