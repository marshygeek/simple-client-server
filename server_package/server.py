from threading import Thread
import socket

from logging import info
from time import sleep

from server_package.utils import *
from server_package.config import *


def do_some_stuffs_with_input(input_string):
    info("Processing that nasty input!")
    return input_string[::-1]


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    info('socket created')

    try:
        sock.bind((HOST, PORT))
        info('binding complete')
    except socket.error as err:
        logging.error('unexpected error occurred while binding: {}'.format(err))
        exit(1)

    sock.listen(MAX_CONNECTIONS_AMOUNT)
    info('Socket now listening')

    while True:
        conn, address = sock.accept()
        info('Accepting connection from {}:{}'.format(*address))
        try:
            Thread(target=handle_connection, args=(conn,)).start()
        except KeyboardInterrupt:
            break
        except Exception as err:
            logging.error('unexpected error occurred while handling connection: {}'.format(err))

    sock.close()


def handle_connection(conn: socket.socket):
    sleep(6)
    from_client = receive_msg(conn)

    msg = from_client
    print(msg.count('hey!buddy!'))

    exit(0)
    siz = getsizeof(from_client)
    if siz >= MAX_BUFFER_SIZE:
        info('The length of input is probably too long: {}'.format(siz))

    input_from_client = from_client.decode().rstrip()

    res = do_some_stuffs_with_input(input_from_client)
    info("Result of processing {} is: {}".format(input_from_client, res))

    vysl = res.encode("utf8")
    conn.sendall(vysl)
    conn.close()


def client():
    sleep(3)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((HOST, PORT))

    clients_input = ''.join('hey!buddy!' for _ in range(1000))

    send_msg(soc, clients_input)
    # soc.sendall(clients_input.encode())

    sleep(300)

    result_bytes = soc.recv(4096)
    result_string = result_bytes.decode()


if __name__ == '__main__':
    Thread(target=client).start()
    start_server()
