import json
from time import monotonic

DEFAULT_URL = "ws://localhost:19167"
TIMEOUT = 3


class YapsError(Exception):
    pass


def exchange(url, command, *, response=False):
    try:
        from websocket import create_connection
    except ImportError as error:
        raise YapsError("Install websocket-client in the Python environment used by StreamController.") from error

    socket = create_connection(url, timeout=TIMEOUT, suppress_origin=True)
    try:
        socket.send(command)
        if not response:
            return None

        deadline = monotonic() + TIMEOUT
        while (remaining := deadline - monotonic()) > 0:
            socket.settimeout(remaining)
            message = socket.recv()
            if not message:
                raise YapsError("YAPS closed the connection.")
            try:
                payload = json.loads(message)
            except (ValueError, UnicodeError):
                continue
            if isinstance(payload, dict) and payload.get("status") == "ok":
                return payload
            if isinstance(payload, dict) and payload.get("status") == "error":
                raise YapsError(payload.get("message") or "YAPS rejected the command.")
        raise YapsError("YAPS did not send a valid response.")
    finally:
        socket.close(timeout=0)
