import os
import importlib.util
from starlette.middleware.base import BaseHTTPMiddleware


def setup_middlewares(app):
    middleware_dir = os.path.dirname(__file__)
    for filename in os.listdir(middleware_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove the ".py" extension
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(middleware_dir, filename)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseHTTPMiddleware)
                    and attr != BaseHTTPMiddleware
                ):
                    app.add_middleware(attr)


"""
For an example on how to construct a middleware file, see /backend/middleware/request_logger.py
"""
