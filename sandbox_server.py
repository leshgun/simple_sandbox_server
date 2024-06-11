# pylint: disable=fixme
"""
    Sandbox server module
"""

import logging

from os import replace as os_replace
from sys import exit as sys_exit, argv as sys_argv
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from pathlib import Path
from re import finditer
from json import loads as json_loads
from base64 import b64encode, b64decode


class SandboxServer:
    """
    Sanbox server
    """

    SOCKET_BUFFER_PER_CLIENT = 1 * 1024
    STANDART_RESPONSE = "Got it!"
    DEFAULT_THREADS_NUM = 5

    def __init__(
        self,
        threads_num: int = DEFAULT_THREADS_NUM,
        bind_ip: str = "127.0.0.1",
        bind_port: int = 15000,
        logger: logging.Logger = lambda: None,
        quarantine_directory: str = "./quarantine_files",
    ) -> None:
        self.threads_num = threads_num or self.DEFAULT_THREADS_NUM
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.logger = logger
        self.quarantine_directory = quarantine_directory
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.bind_ip, self.bind_port))
        if self.threads_num < 1:
            self.threads_num = self.DEFAULT_THREADS_NUM
            self.logger.warning("Threads number must be greater than 0")
        self.logger.info("Server has been initialized.")
        self.logger.info(f"--- Ip: {self.bind_ip}")
        self.logger.info(f"--- Port: {self.bind_port}")
        self.logger.info(f"--- Threads num: {self.threads_num}")

    def start(self) -> None:
        """
        Start the server
        """
        self.server.listen(self.threads_num)
        self.logger.info("The server has started listening.")
        while True:
            try:
                client, addr = self.server.accept()
                self.logger.info(f"Accepted connection from: {addr[0]}:{addr[1]}")
                client_handler = Thread(target=self.handler, args=(client,))
                client_handler.start()
            except KeyboardInterrupt:
                break
        self.stop()

    def stop(self) -> None:
        """
        Stop the server
        """
        self.logger.info("The server has been stopped.")
        self.server.close()

    def handler(self, client: socket) -> None:
        """
        Handler for clients stdin
        """
        # TODO: Decomposite this method
        request = client.recv(self.SOCKET_BUFFER_PER_CLIENT)
        request = b64decode(request)
        request = request.decode()
        request = json_loads(request)
        self.logger.info(f"Received: {request}")
        response = self.run_request(request)
        client.send(b64encode((response or self.STANDART_RESPONSE).encode()))
        client.close()

    def run_request(self, data: dict) -> str:
        """
        Parse request from client and run method
        """
        allowed_commands = {
            "check_local_file": self.check_local_file,
            "quarantine_local_file": self.quarantine_local_file,
        }
        command, args = data["command"], data["args"]
        if command not in allowed_commands:
            self.logger.warning("Unrecognized command: %s", command)
            return "Unrecognized command..."
        self.logger.info(f'Run "{command}" script.')
        response = (allowed_commands[command])(**args) or "Got it!"
        return response

    def check_local_file(self, **kwargs) -> str:
        """
        Check file for the viruses or vulnerabilities
        """
        filepath = kwargs.get("filepath", None)
        signature = kwargs.get("signature", None)
        if not (filepath and signature):
            self.logger.warning("Not enought arguments...")
            return "Not enought arguments..."
        text = self._read_local_file(filepath)
        if not text:
            return "File does not exists or is empty."
        shifts = [s.start() for s in finditer(signature, text)]
        self.logger.info("Found shifts in file: %s", filepath)
        self.logger.info("--- Signature: %s", signature)
        self.logger.info("--- Shifts: %s", shifts)
        return str(shifts)

    def quarantine_local_file(self, **kwargs):
        """
        Send file to quarantine
        """
        filepath = kwargs.get("filepath", None)
        if not filepath:
            self.logger.warning("Not enought arguments...")
            return "Not enought arguments..."
        filename = filepath.split("/")[-1].split("\\")[-1]
        result = self._move_local_file(filepath, self.quarantine_directory, filename)
        if not result:
            return "File has been moved to quarantine folder."
        return f"Cant move file to quarantine. \n --- {result}"

    def _move_local_file(
        self, filepath: str, directory: str, filename: str
    ) -> None | bool:
        """
        Move local file to the directory
        """
        self._create_local_directory(directory)
        try:
            os_replace(filepath, f"{directory}/{filename}")
            self.logger.info("File has been moved to directory: %s", directory)
        except Exception as e:
            self.logger.error("Cant move file to directory: %s", directory)
            self.logger.error("--- Error: %s", e)
            return f"Error: {e}"

    def _create_local_directory(self, directory: str) -> None:
        """
        Check and create new directory
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.info("Directory exists: %s", directory)
        except Exception as e:
            self.logger.error("Cant check or create directory: %s", directory)
            self.logger.error("--- Error: %s", e)

    def _read_local_file(self, filepath: str) -> str:
        """
        Read all contents of the file
        """
        try:
            file = open(filepath, "rb")
            data = file.read().decode()
            file.close()
            return data
        except FileNotFoundError:
            self.logger.error("File not found: %s", filepath)
        except Exception as e:
            self.logger.error("Cant read from file: %s", filepath)
            self.logger.error("--- Error: %e", e)
        return ""


def main():
    """
    Single mode
    """

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(module)s: %(message)s",
        handlers=[logging.FileHandler("log.txt", mode="w"), logging.StreamHandler()],
    )
    logger = logging.getLogger()

    kwargs = args_to_kwargs(sys_argv[1:])
    logger.info("Got args from console: %s", kwargs)

    if kwargs and set(kwargs).issubset(["--help", "-h", "-?"]):
        print_help()
        return

    threads_num = kwargs.get("--threads")
    if threads_num:
        try:
            threads_num = int(threads_num)
        except (ValueError, TypeError):
            logger.error("Threads argument must be an integer")
            return

    quarantine_dir = kwargs.get("--quarantine-dir", "./quarantine_files")

    server = SandboxServer(
        threads_num=threads_num,
        quarantine_directory=quarantine_dir,
        logger=logger,
    )
    Thread(target=server.start, daemon=True).start()

    while True:
        try:
            inp = input()
            logger.info("Got input on server: %s", inp)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
            sys_exit(0)


def print_help() -> None:
    """
    Return help of this module
    """
    options = {
        "threads": (
            "number of logial threads (is equivalent to the number of "
            + "simultaneous connections to the server)"
        ),
        "quarantine-dir": "path where the quarantine files will be stored",
        "help": "print this help",
    }
    print(f"""
    Simple sandbox server
    Usage: python3 sandbox_server.py [option=value]
    
    Options:
    --threads        : {options['threads']}
    --quarantine-dir : {options['quarantine-dir']}
    -?, -h, --help   : {options['help']}
    """)


def args_to_kwargs(args: str) -> dict:
    """
    Parser list ['a', 'b=c', 'd'] to {'a': None, 'b': 'c', 'd': None}
    """
    kwargs = {}
    for arg in args:
        kv = arg.split("=", 1)
        if len(kv) > 1:
            kwargs[kv[0]] = kv[1]
        else:
            kwargs[kv[0]] = None
    return kwargs


if __name__ == "__main__":
    main()
