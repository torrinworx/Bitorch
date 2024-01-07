# General and miscelanious utility tools used by any file in the repo
import os
import configparser

class Utils:
    @staticmethod
    def load_config():
        # Determine the environment
        env = os.getenv('ENV', 'development').lower()

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
