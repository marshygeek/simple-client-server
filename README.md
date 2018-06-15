# Usage
run server:

`python server.py`

send request as client:

e.g:

`python client.py 1 -b -c 2 -arg my_argument`

# Client parameters
You can send simple and batch requests.

Available commands:

- Reverse argument
- Permute argument

You can run:
`python client.py --help`

to see parameters description

# Server side
- Server runs one thread for each new connection
- Tasks are processed parallel to connections handling
- Order of processing tasks is serial (one worker for one queue)