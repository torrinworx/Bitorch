from api.pex import PexTasks


class StartupTasks:
    @staticmethod
    async def run():
        await PexTasks.startup()
