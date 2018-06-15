from sys import path
from os.path import dirname, abspath
from time import sleep

# setting working directory
work_dir = dirname(dirname(dirname(abspath(__file__))))
path.append(work_dir)

from client_package.config import *
from client_package.requests import *
from server_package.server import find_task, start_server
from server_package.worker import Worker
from structs import Task, Command, Request


class Namespace:
    def __init__(self, type, arg, command):
        self.type = type
        self.arg = arg
        self.command = command
        self.task_id = None


def test_find_task():
    response1 = {'success': True}
    response2 = {'success': False, 'msg': 'task is not found'}

    worker = Worker()

    task1 = Task('', Command.REVERSE)
    task2 = Task('', Command.REVERSE)
    worker.push_task(task1)

    assert find_task(worker, task1.id) == response1
    assert find_task(worker, task2.id) == response2


def test_server_interaction():
    worker = Worker()
    run_daemon(start_server, (worker,))
    sleep(3)

    args = Namespace(type=Request.CREATE_TASK, arg='argument', command=Command.REVERSE)
    run_batch_request(args, args.arg[::-1])

    args = Namespace(type=Request.CREATE_TASK, arg='argument', command=Command.PERMUTE)
    run_batch_request(args, 'raugemtn')


def run_batch_request(args, known_result: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    task_id = create_task(sock, args, batch_mode=True)
    assert task_id is not None

    task_status = Status.IN_QUEUE
    args.type = Request.GET_STATUS
    args.task_id = task_id
    while task_status != Status.COMPLETE:
        task_status = get_status(sock, args)
        assert task_status is not None

        sleep(BATCH_SLEEP_TIME)

    args.type = Request.GET_RESULT
    task_result = get_result(sock, args, is_stop=True)
    assert task_result == known_result

    sock.close()
