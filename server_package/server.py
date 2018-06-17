from logging import info
from sys import path
from os.path import dirname, abspath

# setting working directory
work_dir = dirname(dirname(abspath(__file__)))
path.append(work_dir)

from utils import *
from structs import *
from server_package.worker import Worker
from server_package.config import *


def start_server(worker: Worker):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    info('socket created')

    try:
        sock.bind((HOST, PORT))
        info('binding complete')
    except socket.error as err:
        logging.error('unexpected error occurred while binding: {}'.format(err))
        return

    sock.listen(MAX_CONNECTIONS_AMOUNT)
    info('socket is now listening')

    worker.start()
    info('worker started')

    while True:
        conn, address = sock.accept()
        info('accepting connection from {}:{}'.format(*address))
        try:
            run_daemon(handle_request, (conn, worker))
        except KeyboardInterrupt:
            break
        except Exception as err:
            logging.error('unexpected error occurred while handling connection: {}'.format(err))

    sock.close()
    info('socket closed')


def handle_request(conn: socket.socket, worker: Worker):
    msg = receive_msg(conn)
    request = loads(msg)

    if request['batch_mode']:
        while True:
            send_response(conn, worker, request)

            msg = receive_msg(conn)
            if msg is None or 'stop' in request:
                break

            request = loads(msg)
    else:
        send_response(conn, worker, request)

    conn.close()


def send_response(conn: socket.socket, worker: Worker, request: dict):
    response = {}

    if request['type'] != Request.CREATE_TASK:
        request['task_id'] = get_clean_task_id(request['task_id'])

    if request['type'] == Request.CREATE_TASK:
        task = Task(request['argument'], request['command'])
        is_pushed = worker.push_task(task)

        if is_pushed:
            response['success'] = True
            response['task_id'] = task.id
        else:
            response['success'] = False
            response['msg'] = 'task queue is full, try again later'
    elif request['type'] == Request.GET_STATUS:
        task_id = request['task_id']
        response = find_task(worker, task_id)

        if response['success']:
            result = worker.get_result(task_id)
            response['status'] = result.status
    else:
        task_id = request['task_id']
        response = find_task(worker, task_id)

        if response['success']:
            result = worker.get_result(task_id)

            if result.status == Status.COMPLETE:
                response['result'] = result.value

                worker.remove_result(task_id)
            else:
                response['success'] = False
                response['msg'] = 'task is not complete yet'

    dumped_resp = dumps(response)
    send_msg(conn, dumped_resp)


def find_task(worker: Worker, task_id: str) -> dict:
    is_present = worker.is_present(task_id)

    response = {}
    if is_present:
        response['success'] = True
    else:
        response['success'] = False
        response['msg'] = 'task is not found'

    return response


if __name__ == '__main__':
    init_worker = Worker()
    start_server(init_worker)
