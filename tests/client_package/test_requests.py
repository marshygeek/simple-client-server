from sys import path
from os.path import dirname, abspath
from time import sleep

# setting working directory
work_dir = dirname(dirname(dirname(abspath(__file__))))
path.append(work_dir)

from client_package.config import *
from client_package.requests import *
from server_package.server import start_server
from server_package.config import TASK_QUEUE_SIZE, WORKER_SLEEP_TIME
from server_package.worker import Worker
from structs import Command, Request, Task


class Namespace:
    def __init__(self, type, arg, command):
        self.type = type
        self.arg = arg
        self.command = command
        self.task_id = None


def test_requests():
    worker = Worker(use_fake_process=False)
    run_daemon(start_server, (worker,))
    sleep(3)

    args = Namespace(type=Request.CREATE_TASK, arg='argument', command=Command.REVERSE)
    task_id = run_request(args, create_task)
    assert task_id is not None

    args.type = Request.GET_STATUS
    args.task_id = 'random id'
    result = run_request(args, get_status)
    assert result is None

    args.task_id = task_id
    status = run_request(args, get_status)
    assert isinstance(status, Status)
    # wait for task completion
    sleep(WORKER_SLEEP_TIME + 2)

    args.type = Request.GET_RESULT
    args.task_id = 'random id'
    result = run_request(args, get_result)
    assert result is None

    args.task_id = task_id
    result = run_request(args, get_result)
    assert result == 'argument'[::-1]


def run_request(args, request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    result = request(sock, args)

    sock.close()
    return result
