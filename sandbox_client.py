"""
    Sandbox client module
"""

import logging

from sys import argv
from socket import (socket, AF_INET, SOCK_STREAM)
from json import dumps
from base64 import (b64decode, b64encode)

class SandboxClient:
    """
        Sandbox class
    """

    SOCKET_BUFFER = 1 * 1024
    CONSOLE_COMMANDS = ['check_local_file', 'quarantine_local_file']

    _is_connected : bool = False

    def __init__(
            self,
            server_ip:str = '127.0.0.1',
            server_port:int = 15000,
            logger:logging.Logger = lambda: None,
            ) -> None:
        self.server_ip = server_ip
        self.server_port = server_port
        self.logger = logger
        self.client = socket(AF_INET, SOCK_STREAM)
        self.logger.info('Client has been initialized.')

    def check_local_file(
            self,
            filepath:str = None,
            signature:str = None,
            **kwargs) -> str | None:
        """
            Send file on the server to check
        """
        if not filepath:
            self.logger.warning('Needs "filepath" argument.')
            return
        if not signature:
            self.logger.warning('Needs "signature" argument')
            return
        data = {
            'command': 'check_local_file',
            'args': {
                'filepath': filepath,
                'signature': signature
            }
        }
        self._send_to_server(dumps(data))
        return self._recv_response()

    def quarantine_local_file(
            self,
            filepath:str = None,
            **kwargs) -> str | None:
        """
            Send command to server for quarantine the file
        """
        if not filepath:
            self.logger.warning('Needs "filepath" argument.')
            return
        data = {
            'command': 'quarantine_local_file',
            'args': {
                'filepath': filepath
            }
        }
        self._send_to_server(dumps(data))
        return self._recv_response()

    def parse_command(self, command:str, **kwargs) -> None:
        """
            Parse command in string, and execute it.
        """
        # pub_func = [f for f in dir(self) if f[0] != '_']
        pub_func = self.CONSOLE_COMMANDS
        if command not in pub_func:
            self.logger.warning('Command is not recognized: %s', command)
            return
        func = getattr(self, command)
        if not callable(func):
            self.logger.warning('Wrong function: %s', command)
            return
        self.logger.info('Command parsed from string: %s', command)
        self.logger.info('With arguments: %s', kwargs)
        func(**kwargs)

    def _connect(self) -> None:
        """
            Connect to the server
        """
        if self._is_connected:
            self.logger.warning(
                'The client is already connected to the server.'
                )
            return
        self.client.connect((self.server_ip, self.server_port))
        self._is_connected = True
        self.logger.info(
            'Client has been connected to the server '
             + f'{self.server_ip}:{self.server_port}'
            )

    def _disconnect(self) -> None:
        """
            Disconnect from the server
        """
        if not self._is_connected:
            self.logger.warning('The client is not connected to the server.')
            return
        self.client.close()
        self._is_connected = False
        self.logger.info(
            'Client has been disconnected from the server '
             + f'{self.server_ip}:{self.server_port}'
            )

    def _send_to_server(self, data:str) -> None:
        """
            Sending some data to the server
        """
        self._connect()
        self.logger.info('Sending request to the host: %s', data)
        self.client.send(b64encode(data.encode()))

    def _recv_response(self) -> str:
        """
            Recieve data from the host
        """
        self._connect()
        response = self.client.recv(self.SOCKET_BUFFER)
        response = b64decode(response)
        response = response.decode()
        self.logger.info('Recieve from host: %s', response)
        return response



def main():
    """
        Single mode
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(module)s: %(message)s",
        handlers=[
            logging.FileHandler('log.txt', mode='w'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger()

    if argv[1:] and set(argv[1:]).issubset(['--help', '-h', '-?']):
        print_help()
        return

    command = argv[1]
    if not command:
        logger.warning('No command fouded: %s', ' '.join(argv))
        return
    kwargs = args_to_kwargs(argv[2:])
    logger.info('Got args from console: %s', kwargs)

    client = SandboxClient(logger=logger)
    client.parse_command(command, **kwargs)



def print_help() -> None:
    """
        Return help of this module
    """
    options = {
        'help' : 'print this help'
    }
    commands = {
        'check_local_file': 'Check local file "filename" on "signature"',
        'quarantine_local_file': 'Move file "filename" to quarantine directory'
    }
    print(f'''
    Simple sandbox client
    Usage: python3 sandbox_client.py command [option=value]
    
    Commands:
    {commands["check_local_file"]}
    > check_local_file --filename="value" --signature="value"
    {commands["quarantine_local_file"]}
    > quarantine_local_file --filename="value"
    
    Options:
    --filename     : full or relative path to file with filename
    --signature    : signature (string) to find in file  
    -?, -h, --help : {options['help']}
    ''')

def args_to_kwargs(args:str) -> dict:
    """
        Parser list ['a', 'b=c', 'd'] to {'a': None, 'b': 'c', 'd': None}
    """
    kwargs = {}
    for arg in args:
        kv = arg.split('=', 1)
        if len(kv) > 1:
            kwargs[kv[0]] = kv[1]
        else:
            kwargs[kv[0]] = None
    return kwargs



if __name__=='__main__':
    main()
