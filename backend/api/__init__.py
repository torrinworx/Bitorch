import importlib
from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

def mount_api_routes(directory: str, package_name: str) -> None:
    """
    Recursively mounts api routes from all Python files in the specified directory and its subdirectories.

    :param directory: The directory to search for router files.
    :param package_name: The name of the package where the routers are located.
    """
    # Utilizing pathlib for more readable and reliable path handling
    directory_path = Path(directory)

    for item in directory_path.iterdir():
        if item.is_dir():
            # Recursive call to handle subdirectories
            mount_api_routes(str(item), f"{package_name}.{item.name}")
        elif item.suffix == '.py' and item.name != '__init__.py':
            # Importing module and including router if exists
            module_name = item.stem  # Getting filename without extension using pathlib
            module = importlib.import_module(f'.{module_name}', package=package_name)

            # Including router from module if it has one
            if hasattr(module, 'router'):
                router.include_router(module.router)

mount_api_routes(str(Path(__file__).parent.absolute()), __name__)
