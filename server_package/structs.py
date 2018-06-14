from threading import Lock

from enum import Enum
from uuid import uuid4


class SafeDict:
    def __init__(self) -> None:
        self._dict = {}
        self._lock = Lock()

    def put(self, key, val):
        with self._lock:
            self._dict[key] = val

    def get(self, key):
        with self._lock:
            return self._dict[key]

    def remove(self, key):
        with self._lock:
            if key in self._dict:
                del self._dict[key]


class Status(Enum):
    IN_QUEUE = 'in_queue'
    PROCESSING = 'processing'
    COMPLETE = 'complete'


class Command(Enum):
    REVERSE = 1
    PERMUTE = 2


class Task:
    def __init__(self, argument: str, command: Command) -> None:
        self.id = uuid4()
        self.argument = argument
        self.command = command


class Result:
    def __init__(self):
        self.status = Status.IN_QUEUE
        self.value = None

    def complete(self, value):
        self.value = value
        self.status = Status.COMPLETE
