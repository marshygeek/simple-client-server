import logging
from argparse import RawTextHelpFormatter, ArgumentParser

from server_package.config import HOST, PORT

SERVER_HOST, SERVER_PORT = HOST, PORT

BATCH_SLEEP_TIME = 1

parser = ArgumentParser(description='Send requests to the server', formatter_class=RawTextHelpFormatter)

parser.add_argument('--batch', '-b', dest='batch_mode', action='store_true', help='batch mode')
parser.add_argument('--simple', '-s', dest='batch_mode', action='store_false', help='simple mode (default)')
parser.set_defaults(batch_mode=False)

parser.add_argument('type', type=int,
                    help='types of request:\ncreate task: 1,\nget status of the task: 2,\nget result of the task: 3')

parser.add_argument('--task_id', '-id', dest='task_id', type=str, help='id of the task')

parser.add_argument('--command', '-c', dest='command', type=int,
                    help='types of command:\nreverse string: 1,\npermute string: 2')

parser.add_argument('--argument', '-arg', dest='arg', type=str, help='argument to process')

logging.basicConfig(level=logging.INFO)
