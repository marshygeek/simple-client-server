from os.path import dirname, abspath
from sys import path
from time import sleep

# setting working directory
work_dir = dirname(dirname(abspath(__file__)))
path.append(work_dir)

from structs import *
from client_package.config import *
from client_package.requests import *


class Client:
    def __init__(self, args) -> None:
        self._args = args
        self._batch_mode = False
        self._sock = None

    def start(self):
        is_success = handle_wrong_args(self._args)
        if not is_success:
            return

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        info('socket created')

        self._sock.connect((SERVER_HOST, SERVER_PORT))
        info('connected to the server')

        self._batch_mode = self._args.batch_mode and self._args.type == Request.CREATE_TASK
        if self._batch_mode:
            try:
                self.handle_batch_mode()
            except KeyboardInterrupt:
                info('request was canceled by user')
        else:
            self.send_simple_request()

        self._sock.close()
        info('socket closed')

    def send_simple_request(self):
        {
            Request.CREATE_TASK: self.create_task,
            Request.GET_STATUS: self.get_status,
            Request.GET_RESULT: self.get_result,
        }[self._args.type]()

    def handle_batch_mode(self):
        task_id = self.create_task()
        if task_id is None:
            logging.error('failed to start batch request')
            return

        info('created task, task_id: {}'.format(task_id))

        task_status = Status.IN_QUEUE
        self._args.type = Request.GET_STATUS
        self._args.task_id = task_id
        while task_status != Status.COMPLETE:
            task_status = self.get_status()
            if task_status is None:
                logging.error('closing batch request')
                return

            info('\n')

            sleep(BATCH_SLEEP_TIME)

        self._args.type = Request.GET_RESULT
        task_result = self.get_result(is_stop=True)
        if task_result is None:
            logging.error('closing batch request')
            return
        info('completed batch request, result: {}'.format(task_result))

    def create_task(self) -> str:
        return create_task(self._sock, self._args, self._batch_mode)

    def get_status(self) -> Status:
        return get_status(self._sock, self._args, self._batch_mode)

    def get_result(self, is_stop: bool = False) -> str:
        return get_result(self._sock, self._args, self._batch_mode, is_stop)


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


if __name__ == '__main__':
    console_args = parser.parse_args()
    client = Client(console_args)
    client.start()
