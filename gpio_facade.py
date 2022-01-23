import RPi.GPIO as GPIO
import time

# A library: facade class offering more friendly and shorter GPIO calls

class Port:
    def __init__(self, port, direction, pull=GPIO.PUD_UP, initial=GPIO.LOW):
        self.port = port
        self.direction = direction
        self.pull = pull
        self.default = GPIO.HIGH if pull == GPIO.PUD_UP else GPIO.LOW


class Gpio:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.ports = {}

    def setup_in(self, port):
        self.ports[port] = Port(port, GPIO.IN)
        self.__initialize_port(self.ports[port])

    def setup_out(self, port):
        self.ports[port] = Port(port, GPIO.OUT)
        self.__initialize_port(self.ports[port])

    # set high state
    # if duration is given, then go back to low state after the given time in seconds
    #   regardless of the previous state
    def hi(self, port, duration=0):
        GPIO.output(self.ports[port].port, GPIO.HIGH)
        if duration > 0:
            time.sleep(duration)
            GPIO.output(self.ports[port].port, GPIO.LOW)

    # set low state
    # if duration is given, then go back to high state after the given time in seconds
    #   regardless of the previous state
    def lo(self, port, duration=0):
        GPIO.output(self.ports[port].port, GPIO.LOW)
        if duration > 0:
            time.sleep(duration)
            GPIO.output(self.ports[port].port, GPIO.HIGH)

    # get port state as boolean: False if default value (equal PUD), True when non-default
    def get(self, port):
        return GPIO.input(port) != self.ports[port].default

    def input(self, port):
        return GPIO.input(port)

    def cleanup(self):
        GPIO.cleanup()

    def pwm(self, port, hi_percent, stop_condition, freq=200):
        while not stop_condition():
            self.hi(port, 1 / freq * hi_percent / 100)
            self.lo(port, 1 / freq * (100 - hi_percent) / 100)
        GPIO.output(port, self.ports[port].default)

    def sound(self, ):

    def __initialize_port(self, port: Port):
        if port.direction == GPIO.IN:
            GPIO.setup(port.port, port.direction, pull_up_down=port.pull)
        else:
            GPIO.setup(port.port, port.direction, initial=GPIO.LOW)
