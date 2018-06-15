from logging import info
from time import sleep
from sys import path
from os.path import dirname, abspath

# setting working directory
work_dir = dirname(dirname(abspath(__file__)))
path.append(work_dir)

from utils import *
from structs import *
from client_package.config import *
from client_package.requests import create_task, get_status, get_result


def start_client():
    args = parser.parse_args()
    is_success = handle_wrong_args(args)
    if not is_success:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info('socket created')

    sock.connect((SERVER_HOST, SERVER_PORT))
    info('connected to the server')

    if not args.batch_mode or args.type != Request.CREATE_TASK:
        send_simple_request(sock, args)
    else:
        try:
            handle_batch_mode(sock, args)
        except KeyboardInterrupt:
            info('request was canceled by user')

    sock.close()
    info('socket closed')


def handle_wrong_args(args) -> bool:
    is_success = True
    if args.type == Request.CREATE_TASK and args.arg is None:
        logging.error('request\'s type: create task, but no argument found')
        is_success = False
    if args.type == Request.CREATE_TASK and args.command is None:
        logging.error('request\'s type: create task, but no command found')
        is_success = False
    if args.type != Request.CREATE_TASK and args.task_id is None:
        logging.error('no task_id provided')
        is_success = False

    return is_success


def send_simple_request(conn: socket.socket, args):
    {
        Request.CREATE_TASK: create_task,
        Request.GET_STATUS: get_status,
        Request.GET_RESULT: get_result,
    }[args.type](conn, args)


def handle_batch_mode(conn: socket.socket, args):
    task_id = create_task(conn, args, batch_mode=True)
    if task_id is None:
        logging.error('failed to start batch request')
        return

    info('created task, task_id: {}'.format(task_id))

    task_status = Status.IN_QUEUE
    args.type = Request.GET_STATUS
    args.task_id = task_id
    while task_status != Status.COMPLETE:
        task_status = get_status(conn, args)
        if task_status is None:
            logging.error('closing batch request')
            return

        info('\n')

        sleep(BATCH_SLEEP_TIME)

    args.type = Request.GET_RESULT
    task_result = get_result(conn, args, is_stop=True)
    if task_result is None:
        logging.error('closing batch request')
        return
    info('completed batch request, result: {}'.format(task_result))


if __name__ == '__main__':
    start_client()
