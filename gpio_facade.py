import RPi.GPIO as GPIO
import time

# A library: facade class offering more friendly and shorter GPIO calls

class Port:
    def __init__(self, port, direction, pull=GPIO.PUD_UP, initial=GPIO.LOW):
        self.port = port
        self.direction = direction
        self.pull = pull


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
        val = GPIO.input(port)
        return val == GPIO.HIGH and self.ports[port].pull == GPIO.PUD_DOWN or (
            val == GPIO.LOW and self.ports[port].pull == GPIO.PUD_UP
        )

    def input(self, port):
        return GPIO.input(port)

    def cleanup(self):
        GPIO.cleanup()

    def __initialize_port(self, port: Port):
        if port.direction == GPIO.IN:
            GPIO.setup(port.port, port.direction, pull_up_down=port.pull)
        else:
            GPIO.setup(port.port, port.direction, initial=GPIO.LOW)
