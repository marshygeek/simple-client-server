import logging

HOST = '127.0.0.1'
PORT = 8888

MAX_BUFFER_SIZE = 4096
INT_SIZE = 4

MAX_CONNECTIONS_AMOUNT = 10

TASK_QUEUE_SIZE = 15
WORKER_SLEEP_TIME = 3

logging.basicConfig(level=logging.INFO)
