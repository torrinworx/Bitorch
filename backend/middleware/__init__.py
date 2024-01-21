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
Example:

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CustomMiddleware(BaseHTTPMiddleware):
    '''
    CustomMiddleware handles XYZ functionality for each request.
    It modifies/adds/removes ABC aspects from/to the request or response.
    '''

    async def dispatch(self, request: Request, call_next):
        '''
        Process the request, perform actions, and then continue to the next middleware.
        '''
        # Your middleware logic here
        response = await call_next(request)
        # Optionally modify the response here
        return response

"""
