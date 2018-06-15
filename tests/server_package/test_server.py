from sys import path
from os.path import dirname, abspath
from time import sleep

# setting working directory
work_dir = dirname(dirname(dirname(abspath(__file__))))
path.append(work_dir)

from client_package.config import SERVER_HOST, SERVER_PORT
from client_package.requests import *
from server_package.server import find_task, start_server
from server_package.worker import Worker
from structs import Task, Command, Request


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


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
    init_worker = Worker()
    run_daemon(start_server, (init_worker,))
    sleep(3)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    args = Namespace(type=Request.CREATE_TASK, arg='argument', command=Command.REVERSE)

    task_id = create_task(sock, args)
    assert task_id is not None

    args.type = Request.GET_STATUS
    args.task_id = task_id
    status = get_status(sock, args)
    assert status is not None

    while status != Status.COMPLETE:
        status = get_status(sock, args)
        assert status is not None

    args.type = Request.GET_RESULT
    result = get_result(sock, args)
    assert result == 'tnemugra'


test_server_interaction()
