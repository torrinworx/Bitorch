# General and miscelanious utility tools used by any file in the repo
import os
import sys
import json
import socket

import httpx


class Utils:
    @staticmethod
    def load_config():
        # Path to the config file
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(sys.argv[0])), "..", ".config.json"
        )

        # Check if the config file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Read the JSON config file
        with open(config_file, 'r') as file:
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

    env = os.getenv("ENV", "development").lower()
    config = load_config.__func__()
