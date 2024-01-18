import os
import importlib
from fastapi import FastAPI

# TODO: Verify this works properly and that the rate_limit class is working on all endpoints:
def setup_middlewares(app: FastAPI):
    middleware_dir = os.path.dirname(__file__)

    # Iterate through all files in the middleware directory
    for filename in os.listdir(middleware_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = os.path.splitext(filename)[0]

            # Dynamically import the middleware class from the module
            module = importlib.import_module(f".{module_name}", "middleware")
            for name in dir(module):
                cls = getattr(module, name)
                # Add the middleware class to the app
                app.add_middleware(cls)
