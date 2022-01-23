import time
from gpio_facade import Gpio

SENSOR_INPUT = 26
BUZZER_OUTPUT = 19

gpio = Gpio()
gpio.setup_in_lo(SENSOR_INPUT)
gpio.setup_out_hi(BUZZER_OUTPUT)


while True:
    if gpio.get(SENSOR_INPUT):
        gpio.pwm(BUZZER_OUTPUT, 99, 0.1, freq=10)