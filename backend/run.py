import os
import sys
import json
import socket
import importlib
import configparser

from urllib.parse import urlparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

class ServerManager:
    def __init__(self):
        self.env = os.environ.get("NODE_ENV", "development")
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
        config_data = {"backend_port": port}
        config_path = os.path.join(self.exe_dir, '.config')
        with open(config_path, 'w') as file:
            json.dump(config_data, file)

    def check_environment(self):
        if self.env == "production":
            print("> Operating in production mode. Skipping environment checks.")
            return

        if self.env == "development":
            self._development_checks()

        else:
            raise EnvironmentError(f"Unrecognized NODE_ENV value: {self.env}")

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
                importlib.metadata.distribution(package)
            except importlib.metadata.PackageNotFoundError:
                raise ImportError(f"Required package {package} not installed.")

        print("> Environment checks passed successfully.\n")

    def run(self):
        self.check_environment()

        import uvicorn
        from dotenv import load_dotenv

        load_dotenv()

        if self.env == "development":
            parsed_url = urlparse(self.backend_url)
            host, port = parsed_url.hostname, parsed_url.port
            uvicorn.run("main:app", host=host, port=port, reload=True)
        
        else:
            host, port = '0.0.0.0', self.find_available_port(self.default_port)
            self.write_port_to_config(port)
            uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    ServerManager().run()
