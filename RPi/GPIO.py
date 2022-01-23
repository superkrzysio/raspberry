BOARD = 1
OUT = 1
IN = 1
HIGH = 1
LOW = 0
BCM = 0
PUD_UP = 1
PUD_DOWN = 0

ports = {}


def setmode(mode):
    pass

def setup(port, direction, initial=0, pull_up_down=0):
    ports[port] = 0     # set initial


def output(port, state):
    print("[GPIO STUB] Output to GPIO " + str(port) + ": " + str(state))


def setwarnings(flag):
    pass


def input(port):
    if ports.get(port) is None:
        return 0
    else:
        return ports[port]


def set_mock_input(port, state):
    ports[port] = state


def cleanup():
    pass