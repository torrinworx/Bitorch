import os
import ast

import httpx
from utils.utils import Utils


class PexTasks:
    @staticmethod
    async def startup_check():
        # TODO: Peer connection funection, check if peers list is empty
        # then search for more peers to connect to to start things off.
        pass

    @staticmethod
    async def get_my_node():
        node_info = {}

        node_info["ip"] = await Utils.get_ip_address()
        node_info["port"] = os.getenv("BACKEND_PORT")
        node_info["name"] = os.getenv("NODE_NAME")

        return node_info

    @staticmethod
    async def get_source_nodes():
        # Load the entire configuration
        config_dict = Utils.load_config()

        # Select the appropriate section based on the environment
        section = "production" if Utils.env == "production" else "development"

        # Extract source nodes for the specified environment
        if section in config_dict:
            source_nodes = {}
            for key, value in config_dict[section].items():
                # Parse the string value into a dictionary
                try:
                    node_info = ast.literal_eval(value)
                    if isinstance(node_info, dict):
                        source_nodes[key] = node_info
                    else:
                        raise ValueError
                except (SyntaxError, ValueError):
                    raise ValueError(
                        f"Invalid format for node '{key}' in section '{section}'."
                    )
        else:
            raise ValueError(f"Section '{section}' not found in configuration.")

    @staticmethod
    async def request_register():
        source_nodes = Utils.config["development"] if Utils.env == "development" else Utils.config["production"]

        # Try to register with each source node
        for node, node_dict in source_nodes.items():
            print(node)
            # Construct the URL from the node info
            ip = node_dict["ip"]
            port = node_dict["port"]
            name = node_dict["name"]
            url = f"http://{ip}:{port}/register"

            if name == "node0":
                print("Yo mama's node.")
                return  # No registration needed because we are the og source node

            try:
                async with httpx.AsyncClient() as client:
                    print(f"Attempting to register with {url}")
                    response = await client.post(url, json=await PexTasks.get_my_node())

                    if response.status_code == 200:
                        print(f"Registered with {node} successfully.\n")
                    else:
                        print(f"Failed to register with {node}: {response.text}\n")
            except Exception as e:
                print(f"Error registering with {node}: {e}\n")

    @staticmethod
    async def update_peer_list():
        # Implement the logic to update the peer list
        pass

    @staticmethod
    async def send_health_checks():
        print("Scheduled health check function ran")
        return False
        # Implement the logic to send health checks
