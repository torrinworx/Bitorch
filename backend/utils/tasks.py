from backend.api.pex.pex import PexTasks


class StartupTasks:
    @staticmethod
    async def run():
        await PexTasks.startup()
