import os

from api.pex.tasks import PexTasks


class StartupTasks:
    @staticmethod
    async def run():
        await PexTasks.startup_check()

        # If in development, run request_register if in docker network after 10 seconds to wait for other nodes to get setup:
        if os.environ.get("ENV", "development").lower() == "development":
            await PexTasks.request_register()

        else:
            # Register with source production source nodes in .config
            pass

