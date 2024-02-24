import os
import sys
import socket
import configparser
from urllib.parse import urlparse
import importlib.metadata as importlib_metadata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))


class ServerManager:
    def __init__(self):
        self.env = os.environ.get("ENV", "development").lower()
        self.default_port = int(os.getenv("DEFAULT_PORT", 8000))
        self.backend_url = os.getenv("BACKEND_URL")
        self.exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    def _find_available_port(self, start_port):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(("localhost", port))
                if result != 0:  # Port is available
                    return port
                port += 1

    def _environment_check(self):
        if self.env == "production":
            print("> Operating in production mode. Skipping environment checks.")
            return

        if self.env == "development":
            self._development_checks()

        else:
            raise EnvironmentError(f"Unrecognized ENV value: {self.env}")

    @staticmethod
    def _parse_pipfile_for_packages(pipfile_path):
        required_packages = set()
        with open(pipfile_path, 'r') as f:
            lines = f.readlines()
            in_packages_section = False
            for line in lines:
                if line.strip() == "[packages]":
                    in_packages_section = True
                    continue
                if in_packages_section:
                    if line.strip() == "":
                        break  # Empty line, end of packages section
                    if "=" in line:
                        # Assume that we have a package definition line
                        package_name = line.split('=')[0].strip()
                        required_packages.add(package_name.strip('"'))
        return required_packages

    def _development_checks(self):
        print("> Operating in development mode. Initiating environment checks...")

        if not os.path.exists("Pipfile"):
            raise EnvironmentError("Pipfile not found. Please ensure it exists.")

        if "PIPENV_ACTIVE" not in os.environ:
            raise EnvironmentError("Script not running within a Pipenv shell.")

        required_packages = self._parse_pipfile_for_packages("Pipfile")

        for package in required_packages:
            try:
                importlib_metadata.distribution(package)
            except importlib_metadata.PackageNotFoundError:
                raise ImportError(f"Required package {package} not installed.")

        print("> Environment checks passed successfully.\n")

    def run(self):
        self._environment_check()

        import uvicorn
        from dotenv import load_dotenv
        from backend.main import app

        load_dotenv()

        if self.env == "development":
            parsed_url = urlparse(self.backend_url)
            host, port = parsed_url.hostname, parsed_url.port
            uvicorn.run("main:app", host=host, port=port, reload=True)
        else:
            host, port = "0.0.0.0", self._find_available_port(self.default_port)
            uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    ServerManager().run()
