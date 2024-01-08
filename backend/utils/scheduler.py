import asyncio
from rocketry import Rocketry
from utils.tasks import PexTasks

app = Rocketry(execution="async")

@app.task('every 5 seconds')
async def run_health_check():
    result = await PexTasks.request_register()
