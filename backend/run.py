import os
import sys
import socket
import configparser
from urllib.parse import urlparse
import importlib.metadata as importlib_metadata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

class ServerManager:
    def __init__(self):
        self.env = os.environ.get("ENV", "development")
        self.default_port = int(os.getenv("DEFAULT_PORT", 8000))
        self.backend_url = os.getenv("BACKEND_URL")
        self.exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    def find_available_port(self, start_port):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                if result != 0:  # Port is available
                    return port
                port += 1

    def write_port_to_config(self, port):
        config_file = os.path.join(self.exe_dir, '../', '.config')
        # Create a config parser object
        config = configparser.ConfigParser()

        # Read the existing config file
        config.read(config_file)

        # Add or update the backend port
        if 'backend' not in config:
            config['backend'] = {}
        config['backend']['port'] = str(port)

        # Write the updated configuration back to the file
        with open(config_file, 'w') as file:
            config.write(file)

    def _environment_check(self):
        if self.env == "production":
            print("> Operating in production mode. Skipping environment checks.")
            return

        if self.env == "development":
            self._development_checks()

        else:
            raise EnvironmentError(f"Unrecognized ENV value: {self.env}")

    def _development_checks(self):
        print("> Operating in development mode. Initiating environment checks...")

        if not os.path.exists("Pipfile"):
            raise EnvironmentError("Pipfile not found. Please ensure it exists.")

        if 'PIPENV_ACTIVE' not in os.environ:
            raise EnvironmentError("Script not running within a Pipenv shell.")

        config = configparser.ConfigParser()
        config.read('Pipfile')
        required_packages = {pkg.strip('"') for pkg in config['packages']}

        for package in required_packages:
            try:
                importlib_metadata.distribution(package)
            except importlib_metadata.PackageNotFoundError:
                raise ImportError(f"Required package {package} not installed.")

        print("> Environment checks passed successfully.\n")
    
    async def _run_server(self, app_instance, host, port):
        # NOTE: Import here as to not interfear with the environment_check
        import asyncio
        import uvicorn
        from utils.scheduler import app as app_rocketry      
        
        class Server(uvicorn.Server):
            """
            Customized uvicorn.Server

            Uvicorn server overrides signals, and we need to include
            Rocketry to the signals.
            """
            def handle_exit(self, sig: int, frame) -> None:
                app_rocketry.session.shut_down()
                return super().handle_exit(sig, frame)

        config = uvicorn.Config(app_instance, host=host, port=port, workers=1, loop="asyncio")
        server = Server(config=config)

        api = asyncio.create_task(server.serve())
        sched = asyncio.create_task(app_rocketry.serve())

        await asyncio.wait([sched, api])

    def run(self):
        self._environment_check()

        # NOTE: Import here as to not interfear with the environment_check
        import asyncio
        from dotenv import load_dotenv
        
        load_dotenv()

        self.write_port_to_config(self.default_port)
        host, port = ('0.0.0.0', self.find_available_port(self.default_port))

        if self.env == "development":
            parsed_url = urlparse(self.backend_url)
            host, port = parsed_url.hostname, parsed_url.port
            app_instance = "main:app"
        elif self.env == "production":
            app_instance = app

        asyncio.run(self._run_server(app_instance, host, port))

if __name__ == "__main__":
    ServerManager().run()
