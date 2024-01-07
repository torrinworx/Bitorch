# Manage async tasks like pex register and health checks
# NOTE: expand this functionality in the future maybe to keep the code more organized
# by creating a /backend/tasks folder where tasks.py is the mount point for all tasks
# classes
# NOTE: make it so that each function in the startup tasks can be run scheduled, or 
# called by a function elsewhere in the codebase.

import asyncio

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
        # Implement the logic to request to be registered on a peer
        pass

    @staticmethod
    async def update_peer_list():
        # Implement the logic to update the peer list
        pass

    @staticmethod
    async def send_health_checks():
        print("Scheduled health check function ran")
        # Implement the logic to send health checks
