from rocketry import Rocketry
from utils.tasks import PexTasks

app = Rocketry(execution="async")

@app.task('every 5 seconds')
async def run_health_check():
    await PexTasks.send_health_checks()
