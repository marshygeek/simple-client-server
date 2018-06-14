from queue import Queue
from threading import Lock
from enum import Enum
from uuid import uuid4

from server_package.config import TASK_QUEUE_SIZE


class Worker:
    def __init__(self) -> None:
        self.queue = Queue(TASK_QUEUE_SIZE)


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
    IN_QUEUE = 1
    PROCESSING = 2
    COMPLETE = 3


class Task:
    def __init__(self, argument: str) -> None:
        self.id = uuid4()
        self.argument = argument
        self.status = Status.IN_QUEUE
