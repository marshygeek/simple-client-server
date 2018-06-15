import socket
from json import loads, dumps
from os.path import dirname, abspath
from struct import pack, unpack
from sys import getsizeof, path
from threading import Thread
from typing import Tuple, Callable

from server_package.config import INT_SIZE

# setting working directory
work_dir = dirname(dirname(abspath(__file__)))
path.append(work_dir)


def send_msg(conn: socket.socket, msg: str) -> None:
    raw_msg = msg.encode()
    msg_size = getsizeof(raw_msg)

    packed_msg = pack('>I', msg_size) + raw_msg

    conn.sendall(packed_msg)


def receive_msg(conn: socket.socket) -> str:
    raw_msg_size = receive_all(conn, INT_SIZE)
    msg_size = unpack('>I', raw_msg_size)[0]

    raw_msg = receive_all(conn, msg_size)
    return raw_msg.decode()


def receive_all(conn: socket.socket, n: int) -> bytes:
    data = b''
    data_size = 0
    while data_size < n:
        packet = conn.recv(n - data_size)
        if not packet:
            break

        data += packet
        data_size = getsizeof(data)
    return data


def run_daemon(target: Callable, args: Tuple = ()) -> None:
    thread = Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


def send_receive(conn: socket.socket, request: dict) -> dict:
    dumped_req = dumps(request)
    send_msg(conn, dumped_req)

    msg = receive_msg(conn)
    return loads(msg)
