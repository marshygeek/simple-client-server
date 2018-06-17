from queue import Queue
from time import sleep

from server_package.config import TASK_QUEUE_SIZE, WORKER_SLEEP_TIME
from structs import *
from utils import run_daemon


class Worker:
    def __init__(self, queue_size=TASK_QUEUE_SIZE, use_fake_process=True) -> None:
        self._queue = Queue(queue_size)
        self._results = SafeDict()

        self._use_fake_process = use_fake_process

    def start(self):
        run_daemon(self._process_tasks)

    def _process_tasks(self):
        while True:
            if not self._queue.empty():
                task = self._queue.get()  # type: Task

                result = self._results.get(task.id)  # type: Result
                result.status = Status.PROCESSING

                value = self._process_task(task)
                result.complete(value)

            sleep(WORKER_SLEEP_TIME)

    def _process_task(self, task: Task) -> str:
        if task.command == Command.REVERSE:
            result = task.argument[::-1]

            if self._use_fake_process:
                sleep(3)
        else:
            arg = list(task.argument)
            for idx in range(1, len(arg), 2):
                arg[idx - 1], arg[idx] = arg[idx], arg[idx - 1]

            result = ''.join(arg)

            if self._use_fake_process:
                sleep(7)
        return result

    def push_task(self, task: Task) -> bool:
        if not self._queue.full():
            self._results.put(task.id, Result())
            self._queue.put(task)
            return True
        return False

    def is_present(self, task_id: str) -> bool:
        return self._results.is_present(task_id)

    def get_result(self, task_id: str) -> Result:
        return self._results.get(task_id)

    def remove_result(self, task_id: str) -> None:
        self._results.remove(task_id)
