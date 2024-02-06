from functools import wraps

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Scheduler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Scheduler, cls).__new__(cls)
            cls._instance.sched = AsyncIOScheduler()
        return cls._instance

    def run(self):
        self.sched.start()

    def shutdown(self):
        self.sched.shutdown()

    def schedule_task(self, *args, **kwargs):
            def decorator(func):
                @wraps(func)
                async def wrapper(*func_args, **func_kwargs):
                    return await func(*func_args, **func_kwargs)

                # Check if a job with the given ID already exists
                try:
                    existing_job = self.sched.get_job(kwargs.get('id'))
                    if existing_job:
                        # Handle the existing job (e.g., remove it, log a warning, etc.)
                        self.remove_task(existing_job.id)
                except Exception as e:
                    print(f"Error checking for existing task: {e}")

                self.sched.add_job(wrapper, *args, **kwargs)
                return wrapper

            return decorator

    def remove_task(self, task_id):
        try:
            self.sched.remove_job(task_id)
        except Exception as e:
            print(f"Error removing task: {e}")


# This will always return the same instance
scheduler = Scheduler()


# Example usage:
# from utils.scheduler import scheduler
# @scheduler.schedule_task(
#     trigger="interval", seconds=5, id="request_register_source_peer"
# )
# async def request_register_source_peer():
#     result = await PexTasks.request_register()

#     if result:
#         scheduler.remove_task(task_id="request_register_source_peer")
