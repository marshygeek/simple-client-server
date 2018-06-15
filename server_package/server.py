from logging import info

from utils import *
from server_package.worker import Worker
from server_package.config import *
from structs import *


def start_server():
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
            run_daemon(handle_request, (conn,))
        except KeyboardInterrupt:
            break
        except Exception as err:
            logging.error('unexpected error occurred while handling connection: {}'.format(err))

    sock.close()
    info('socket closed')


def handle_request(conn: socket.socket):
    msg = receive_msg(conn)
    request = loads(msg)

    if request['batch_mode']:
        while True:
            send_response(conn, request)

            msg = receive_msg(conn)
            request = loads(msg)
            if 'stop' in request:
                break
    else:
        send_response(conn, request)

    conn.close()


def send_response(conn: socket.socket, request: dict):
    response = {}
    if request['type'] == Request.CREATE_TASK:
        task = Task(request['argument'], request['command'])
        is_pushed = worker.push_task(task)

        if is_pushed:
            response['success'] = True
            response['id'] = task.id
        else:
            response['success'] = False
            response['msg'] = 'task queue is full, try again later'
    elif request['type'] == Request.GET_STATUS:
        task_id = request['id']
        response = find_task(task_id)

        if response['success']:
            result = worker.results.get(task_id)
            response['status'] = result.status
    else:
        task_id = request['id']
        response = find_task(task_id)

        if response['success']:
            result = worker.results.get(task_id)

            if result.status == Status.COMPLETE:
                response['result'] = result.value
            else:
                response['success'] = False
                response['msg'] = 'task is not complete yet'

    dumped_resp = dumps(response)
    send_msg(conn, dumped_resp)


def find_task(task_id: str) -> dict:
    is_present = worker.results.is_present(task_id)

    response = {}
    if is_present:
        response['success'] = True
    else:
        response['success'] = False
        response['msg'] = 'task is not found'

    return response


if __name__ == '__main__':
    worker = Worker()
    start_server()
