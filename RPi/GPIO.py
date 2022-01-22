BOARD = 1
OUT = 1
IN = 1
HIGH = 1
LOW = 0
BCM = 0

ports = {}


def setmode(mode):
    pass

def setup(port, direction):
    ports[port] = 0     # set initial


def output(port, state):
    print("[GPIO STUB] Output to GPIO " + str(port) + ": " + str(state))


def setwarnings(flag):
    pass


def input(port):
    return 0


def set_mock_input(port, state):
    ports[port] = state