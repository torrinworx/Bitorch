import os
import sys
import time
import signal
import socket
import threading
from urllib.parse import urlparse
import importlib.metadata as importlib_metadata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))


class ServerManager:
    """Manages the server environment and process for a web application.

    This class is responsible for setting up the server environment, ensuring
    required packages are installed, and running the server process. It handles
    graceful shutdown of the server on receiving interrupt signals.

    Attributes:
        env (str): Environment for the server ('development' or 'production').
        default_port (int): Default port number for the server.
        backend_url (str): URL for the backend service.
        exe_dir (str): Directory where the executable resides.
        child_process (subprocess.Popen): Reference to the child server process.
        stop_spinner (threading.Event): Event to stop the progress spinner.
    """
    def __init__(self):
        """Initializes the server manager with environment configurations."""
        self.env = os.environ.get("ENV", "development").lower()
        self.default_port = int(os.getenv("DEFAULT_PORT", 8000))
        self.backend_url = os.getenv("BACKEND_URL")
        self.exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.child_process = None
        self.stop_spinner = threading.Event()

    def _find_available_port(self, start_port):
        """Finds an available network port to use.

        Args:
            start_port (int): The starting port number to check for availability.

        Returns:
            int: The first available port number starting from 'start_port'.
        """
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(("localhost", port))
                if result != 0:  # Port is available
                    return port
                port += 1

    def _environment_check(self):
        """Checks and prepares the environment based on the configured mode."""
        if self.env == "production":
            print("> Operating in production mode. Skipping environment checks.")
            return

        if self.env == "development":
            self._development_checks()

        else:
            raise EnvironmentError(f"Unrecognized ENV value: {self.env}")

    @staticmethod
    def _parse_pipfile_for_packages(pipfile_path):
        """Parses a Pipfile to identify required packages.

        Args:
            pipfile_path (str): Path to the Pipfile to parse.

        Returns:
            set: A set of package names extracted from the Pipfile.
        """
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
        """Performs environment checks for development mode."""
        print("> Operating in development mode. Initiating environment checks...")

        if not os.path.exists("Pipfile"):
            raise EnvironmentError("Pipfile not found. Please ensure it exists.")

        required_packages = self._parse_pipfile_for_packages("Pipfile")

        for package in required_packages:
            try:
                importlib_metadata.distribution(package)
            except importlib_metadata.PackageNotFoundError:
                raise ImportError(f"Required package {package} not installed.")

        print("> Environment checks passed successfully.\n")

    def _start_spinner(self):
        """Displays a text-based spinner to indicate progress."""
        spinner = ["-", "\\", "|", "/"]
        idx = 0
        while not self.stop_spinner.is_set():
            print(f"\rExiting... {spinner[idx % len(spinner)]}", end="")
            idx += 1
            time.sleep(0.1)
        # Clear the spinner line after stopping
        print("\r", " " * 20, "\r", end="")

    def _exit(self, signum, frame):
        """Handles graceful shutdown of the application."""
        print("Initiating shutdown...")
        spinner_thread = threading.Thread(target=self._start_spinner)
        spinner_thread.start()

        if self.child_process is not None:
            self.child_process.terminate()
            self.child_process.wait()  # Wait for child process to terminate

        # Signal the spinner to stop and wait for the thread to finish
        self.stop_spinner.set()
        spinner_thread.join()

        print("Successfully exited.")
        sys.exit(0)

    def run(self):
        """Runs the server process and handles graceful shutdown."""
        signal.signal(signal.SIGINT, self._exit)

        self._environment_check()

        import subprocess
        from dotenv import load_dotenv

        load_dotenv()

        parsed_url = urlparse(self.backend_url)
        host, port = parsed_url.hostname, parsed_url.port

        command = [
            "pipenv",
            "run",
            "uvicorn",
            "backend.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]

        if os.getenv("ENV") == "development":
            command.append("--reload")

        try:
            self.child_process = subprocess.Popen(command)
            self.child_process.communicate()
        except KeyboardInterrupt:
            self._exit(None, None)


if __name__ == "__main__":
    ServerManager().run()
