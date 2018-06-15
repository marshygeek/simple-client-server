from logging import info

from utils import *
from structs import Status


def create_task(conn: socket.socket, args, batch_mode: bool = False) -> str:
    request = {
        'type': args.type,
        'argument': args.arg,
        'command': args.command,
        'batch_mode': batch_mode,
    }

    response = send_receive(conn, request)

    task_id = None
    if response['success']:
        task_id = response['task_id']
        info('request completed, task_id: {}'.format(task_id))
    else:
        info('request failed, msg: {}'.format(response['msg']))
    return task_id


def get_status(conn: socket.socket, args, batch_mode: bool = False) -> Status:
    info('getting status, task_id: {}'.format(args.task_id))

    request = {
        'type': args.type,
        'task_id': args.task_id,
        'batch_mode': batch_mode,
    }

    response = send_receive(conn, request)

    status = None
    if response['success']:
        status = Status(response['status'])
        info('request completed, status: {}'.format(status.name))
    else:
        info('request failed, msg: {}'.format(response['msg']))
    return status


def get_result(conn: socket.socket, args, batch_mode: bool = False, is_stop: bool = False) -> str:
    info('getting result, task_id: {}'.format(args.task_id))

    request = {
        'type': args.type,
        'task_id': args.task_id,
        'batch_mode': batch_mode,
    }

    if is_stop:
        request['stop'] = True

    response = send_receive(conn, request)

    result = None
    if response['success']:
        result = response['result']
        info('request completed, result: {}'.format(result))
    else:
        info('request failed, msg: {}'.format(response['msg']))
    return result
