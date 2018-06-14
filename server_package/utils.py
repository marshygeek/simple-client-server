from sys import getsizeof
from socket import socket
from struct import pack, unpack

from server_package.config import INT_SIZE


def send_msg(conn: socket, msg: str) -> None:
    raw_msg = msg.encode()
    msg_size = getsizeof(raw_msg)

    packed_msg = pack('>I', msg_size) + raw_msg

    conn.sendall(packed_msg)


def receive_msg(conn: socket) -> str:
    raw_msg_size = receive_all(conn, INT_SIZE)
    msg_size = unpack('>I', raw_msg_size)[0]

    raw_msg = receive_all(conn, msg_size)
    return raw_msg.decode()


def receive_all(conn: socket, n: int) -> bytes:
    data = b''
    data_size = 0
    while data_size < n:
        packet = conn.recv(n - data_size)
        if not packet:
            break

        data += packet
        data_size = getsizeof(data)
    return data
