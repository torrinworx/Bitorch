import os
import importlib
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware


def setup_middlewares(app: FastAPI):
    middleware_dir = os.path.dirname(__file__)

    # Iterate through all files in the middleware directory
    for filename in os.listdir(middleware_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = os.path.splitext(filename)[0]

            # Dynamically import the middleware class from the module
            module = importlib.import_module(f".{module_name}", "middleware")
            for name in dir(module):
                attribute = getattr(module, name)
                # Ensure that the attribute is a class
                if isinstance(attribute, type):
                    # Check if the class is a subclass of BaseHTTPMiddleware
                    if issubclass(attribute, BaseHTTPMiddleware):
                        # Add the middleware class to the app
                        app.add_middleware(attribute)
