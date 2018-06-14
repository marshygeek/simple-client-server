from queue import Queue
from time import sleep

from server_package.config import TASK_QUEUE_SIZE, WORKER_SLEEP_TIME
from server_package.utils import run_daemon
from server_package.structs import *


class Worker:
    def __init__(self) -> None:
        self.queue = Queue(TASK_QUEUE_SIZE)
        self.results = SafeDict()

    def start(self):
        run_daemon(self._process_tasks)

    def push_task(self, task: Task):
        self.results.put(task.id, Result())
        self.queue.put(task)

    def _process_tasks(self):
        while True:
            if not self.queue.empty():
                task = self.queue.get()  # type: Task

                result = self.results.get(task.id)  # type: Result
                result.status = Status.PROCESSING

                value = self._process_task(task)
                result.complete(value)

            sleep(WORKER_SLEEP_TIME)

    def _process_task(self, task: Task) -> str:
        if task.command == Command.REVERSE:
            result = task.argument[::-1]
            sleep(3)
        else:
            arg = list(task.argument)
            for idx in range(1, len(arg)):
                arg[idx - 1], arg[idx] = arg[idx], arg[idx - 1]

            result = ''.join(arg)
            sleep(7)
        return result
