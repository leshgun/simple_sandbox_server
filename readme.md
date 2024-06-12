# Simple sandbox server and client

The server runs on a socket, and the client connects to it, after which it transmits some commands with arguments in *json* format encoded in *base64* format.

## Starting the server

To start the server, enter the command:

```bash
python3 sandbox_server.py [option=value]
```

Options:

| Option               | Description                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| `--threads`        | number of logial threads (is equivalent to the number of simultaneous connections to the server) |
| `--quarantine-dir` | path where the quarantine files will be stored                                                   |
| `-?, -h, --help`   | print help                                                                                       |

## Statring the client

To start the client, enter the command:

```bash
python3 sandbox_client.py command [option=value]
check_local_file
 --filename="val"
 --signature="val"
```

Commands:

| Command                                               | Description                                     | Result                                                            |
| ----------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| check_local_file --filename="val" --signature="val" | Check local file `filename` on `signature` | An array of signature shift positions                             |
| quarantine_local_file--filename="val"                 | Move file `filename` to quarantine directory | Moves the specified file to thequarantine directory of the server |

Options:

| Option             | Description                                 |
| ------------------ | ------------------------------------------- |
| `--filename`     | full or relative path to file with filename |
| `--signature`    | signature (string) to find in file          |
| `-?, -h, --help` | print this help                             |

## Tests

To run the tests, to make sure that the server is working correctly, you need to run the command:

```bash
python test_sandbox_server.py -v
```

## Todo

- [X] Unit test to check new features in CI/CD
- [X] Code review
