from backend.api.pex.pex_tasks import PexTasks


class StartupTasks:
    @staticmethod
    async def run():
        await PexTasks.startup()
