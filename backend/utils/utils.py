# General and miscelanious utility tools used by any file in the repo
import os
import httpx
import socket
import configparser

class Utils:
    @staticmethod
    def load_config():
        # Determine the environment
        env = os.environ.get('ENV', 'development').lower()

        # Create a config parser object
        config = configparser.ConfigParser()

        # Read the config file
        config.read('config.config')

        # Extract and return the configuration data for the specified environment
        # This will return the source nodes as a dictionary for the specified environment
        section = 'production' if env == 'production' else 'development'
        if section in config:
            source_nodes = {key: value for key, value in config.items(section)}
            return source_nodes
        else:
            raise Exception(f"Configuration section '{section}' not found in config file.")
    
    @staticmethod
    def get_ip_address():
        # Check the environment
        env = os.getenv('ENV', 'development').lower()

        if env == 'production':
            # For production, use an external service to get the public IP
            try:
                response = httpx.get('https://api.ipify.org')
                return response.text if response.status_code == 200 else None
            except httpx.HTTPError:
                return None
        else:
            # For development, return the local IP address
            # This is also suitable for Docker containers communicating within the same network
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
