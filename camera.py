import os.path
import shutil
import sys

import time
import threading

import signals
import RPi.GPIO as GPIO
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

### constants
G_IN1 = 9
G_IN2 = 10
G_POWEROFF = 25
G_MODESWITCH = 8
G_OUT = 24
TARGET = "/home/pi/photos/"
PENDRIVE = "/media/pi/PENDRIVE/"    # usb storage partition label

if not os.path.exists(TARGET):
    os.mkdir(TARGET)

### GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(G_IN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)       # button should ground the signal (send LOW)
GPIO.setup(G_IN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)       #  - no external resistors needed!
GPIO.setup(G_POWEROFF, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #  - uses slightly less power
GPIO.setup(G_MODESWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(G_OUT, GPIO.OUT, initial=GPIO.LOW)


def hi(port):
    GPIO.output(port, GPIO.HIGH)


def lo(port):
    GPIO.output(port, GPIO.LOW)


def notification_signal(duration):
    hi(G_OUT)
    time.sleep(duration)
    lo(G_OUT)


signals = signals.Signals(notification_signal)


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
    signals.bye()
    GPIO.cleanup()
    os.system("sleep 5 && sudo shutdown -P now &")
    sys.exit(0)


button1 = Button()
button1.trigger = lambda: GPIO.input(G_IN1)
button1.action = capture_quality

button2 = Button()
button2.trigger = lambda: GPIO.input(G_IN2)
button2.action = capture_fast

button_off = Button()
button_off.trigger = lambda: GPIO.input(G_POWEROFF)
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

    # dismount everything except /dev/sda - watch out in your setup
    drives = [sd for sd in os.listdir("/dev/") if sd.startswith("sd") and sd != "sda"]
    for drive in drives:
        os.system("umount /dev/" + drive)

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
