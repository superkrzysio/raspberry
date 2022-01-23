import RPi.GPIO as GPIO
import time

# A library: facade class offering more friendly and shorter GPIO calls

class Port:
    def __init__(self, port, direction, pull=GPIO.PUD_UP, initial=GPIO.LOW):
        self.port = port
        self.direction = direction
        self.pull = pull
        self.default = initial

class Gpio:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.ports = {}
        self.sounds = Gpio.Sound()

    # setup IN port, default pull up
    def setup_in(self, port):
        self.ports[port] = Port(port, GPIO.IN)
        self.__initialize_port(self.ports[port])

    # setup IN port, default pull down
    def setup_in_lo(self, port):
        self.ports[port] = Port(port, GPIO.IN, pull=GPIO.PUD_DOWN)
        self.__initialize_port(self.ports[port])

    # setup OUT port, initial LOW
    def setup_out(self, port):
        self.ports[port] = Port(port, GPIO.OUT)
        self.__initialize_port(self.ports[port])

    def setup_out_hi(self, port):
        self.ports[port] = Port(port, GPIO.OUT, initial=GPIO.HIGH)
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

    def pwm(self, port, hi_percent, duration, freq=200):
        t_start = time.time()
        while t_start + duration > time.time():
            self.hi(port, 1 / freq * hi_percent / 100)
            self.lo(port, 1 / freq * (100 - hi_percent) / 100)
        GPIO.output(port, self.ports[port].default)

    # play sound (output high and low) with a given frequency
    # frequencies can be taken from self.sounds object, eg. self.sounds.A1
    # it is not optimal (e.g. sends twice the same signal) but enough for buzzer music
    def playsound(self, port, freq, duration):
        t_start = time.time()
        while t_start + duration > time.time():
            self.hi(port, 1 / freq / 2)
            self.lo(port, 1 / freq / 2)
        GPIO.output(port, self.ports[port].default)

    def __initialize_port(self, port: Port):
        if port.direction == GPIO.IN:
            GPIO.setup(port.port, port.direction, pull_up_down=port.pull)
        else:
            GPIO.setup(port.port, port.direction, initial=port.default)

    class Sound:
        def __init__(self):
            # create attributes with note names, like A0, C2, Eb3, etc
            note_names = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
            for octave in range(0, 5):
                for halftone in range(0, 12):
                    self.__setattr__(note_names[halftone] + str(octave), self.__calculate(octave, halftone))

        @staticmethod
        def __calculate(octave, halftones):
            base_freq = 220
            return base_freq*pow(2, octave+halftones/12)
