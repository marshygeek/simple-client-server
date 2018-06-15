import socket
from json import loads, dumps
import struct
from sys import getsizeof
from threading import Thread
from typing import Tuple, Callable

from server_package.config import INT_SIZE


def send_msg(conn: socket.socket, msg: str) -> None:
    raw_msg = msg.encode()
    msg_size = getsizeof(raw_msg)

    packed_msg = struct.pack('>I', msg_size) + raw_msg

    conn.sendall(packed_msg)


def receive_msg(conn: socket.socket) -> str:
    raw_msg_size = receive_all(conn, INT_SIZE)

    try:
        msg_size = struct.unpack('>I', raw_msg_size)[0]
    except struct.error:
        return None

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
