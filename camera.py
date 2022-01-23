import os.path
import shutil
import sys
import time

import signals
from gpio_facade import Gpio
from picamera import PiCamera

# script for taking photos triggered by a signal and without preview
# can be used for motion-triggered monitoring later, e.g. in car

# uses 1 GPIO port for output signal (e.g. buzzer) and 1 for each sensor (button)
# Use cases:
#   - ready to be started during OS boot
#   - press button1 to make photo in 1st configuration
#   - press button2 to make photo in 2nd configuration
#   - connect USB stick to automatically store all the photos on it, then dismount
#   - get vibration/sound confimations of all actions
#   - graceful shutdown button
#   - TODO: two-state toggle to switch between photo and video

### setup
G_IN1 = 9
G_IN2 = 10
G_POWEROFF = 25
G_MODESWITCH = 8
G_OUT = 24
TARGET = "/home/pi/photos/"
PENDRIVE = "/media/pi/PENDRIVE/"    # usb storage partition label

gpio = Gpio()
gpio.setup_in(G_IN1)
gpio.setup_in(G_IN2)
gpio.setup_in(G_POWEROFF)
gpio.setup_out(G_OUT)

def signal(duration):
    return gpio.hi(G_OUT, duration)

signals = signals.Signals(signal)

if not os.path.exists(TARGET):
    os.mkdir(TARGET)

class Button:
    def __init__(self):
        self.trigger = self.must_configure
        self.action = self.must_configure

    def must_configure(self):
        raise Exception("Not set up correctly")


def capture_quality(camera: PiCamera, stop_condition):
    camera.iso = 200
    camera.drc_strength = "low"
    camera.image_denoise = True

    for i, f in enumerate(camera.capture_continuous(TARGET + 'image-{timestamp:%Y.%m.%d-%H.%M.%S.%f}.jpg')):
        if stop_condition():
            break
        signals.ping(True)


def capture_fast(camera: PiCamera, stop_condition):
    camera.iso = 0
    camera.drc_strength = "off"
    camera.image_denoise = False

    for i, f in enumerate(camera.capture_continuous(TARGET + 'image-{timestamp:%Y.%m.%d-%H.%M.%S.%f}-burst.jpg', burst=True)):
        if stop_condition():
            break
        signals.ping(True)


def shutdown(camera: PiCamera, stop_condition):
    time.sleep(1)       # bad pattern to wait for other threads playing sounds
    signals.bye()
    gpio.cleanup()
    os.system("sleep 5 && sudo shutdown -P now &")
    sys.exit(0)


button1 = Button()
button1.trigger = lambda: gpio.get(G_IN1)
button1.action = capture_quality

button2 = Button()
button2.trigger = lambda: gpio.get(G_IN2)
button2.action = capture_fast

button_off = Button()
button_off.trigger = lambda: gpio.get(G_POWEROFF)
button_off.action = shutdown

buttons = [button1, button2, button_off]


def check_pendrive():
    if not os.path.exists(PENDRIVE):
        return

    signals.welcome()

    for file in os.listdir(TARGET):
        try:
            shutil.move(TARGET + file, PENDRIVE)
        except:
            signals.alert()

    # /dev/sda is the default and the only device in my setup
    os.system("umount /dev/sda1")

    signals.win()


### script start
with PiCamera() as cam:
    cam.resolution = (2592, 1944)
    signals.welcome()

    # main polling loop
    while True:
        for button in buttons:
            if button.trigger():
                signals.ping(True)
                try:
                    button.action(cam, lambda: not button.trigger())
                except:
                    signals.alert()

        check_pendrive()

        # todo: using a toggled switch will require interrupts approach or will much complicate this framework
        #  also, interrupts save power
        time.sleep(0.1)
