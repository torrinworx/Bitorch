# Manage async tasks like pex register and health checks
# NOTE: expand this functionality in the future maybe to keep the code more organized
# by creating a /backend/tasks folder where tasks.py is the mount point for all tasks
# classes
# NOTE: make it so that each function in the startup tasks can be run scheduled, or 
# called by a function elsewhere in the codebase.

import httpx
import asyncio
from utils.utils import Utils

class StartupTasks:
    @staticmethod
    async def run():
        await PexTasks.startup_check()

class PexTasks:
    @staticmethod
    async def startup_check():
        # TODO: Peer connection function, check if peers list is empty
        # then search for more peers to connect to to start things off.
        print("Startup check function ran")
    
    @staticmethod
    async def request_register():
        config = Utils.load_config()
        source_nodes = config.get('source_nodes', {})
        
        # Assuming the current node's address is available as a local variable or from config
        current_node_address = Utils.get_ip_address()

        # Register with each source node
        for node, address in source_nodes.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"http://{address}/register", json={"address": current_node_address})
                    
                    if response.status_code == 200:
                        print(f"Registered with {node} successfully.")
                    else:
                        print(f"Failed to register with {node}: {response.text}")
            except Exception as e:
                print(f"Error registering with {node}: {e}")

    @staticmethod
    async def update_peer_list():
        # Implement the logic to update the peer list
        pass

    @staticmethod
    async def send_health_checks():
        print("Scheduled health check function ran")
        # Implement the logic to send health checks
