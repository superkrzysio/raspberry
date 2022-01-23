import os.path
import shutil

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

# PS. strange bug I experienced:
# after connecting any loose wire to input port, it started blinking/fluctuating on/off at 0.5-2Hz
#     - as if it were some antenna
# also happened when I touched the port
# workaround: ground the port/wire through 680k resistor


### constants
GIN1 = 9
GIN2 = 10
GOUT = 24
TARGET = "/home/pi/photos/"
PENDRIVE = "/media/pi/PENDRIVE/"    # usb storage partition label

if not os.path.exists(TARGET):
    os.mkdir(TARGET)

### GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(GIN1, GPIO.IN)
GPIO.setup(GIN2, GPIO.IN)
GPIO.setup(GOUT, GPIO.OUT)


def hi(port):
    GPIO.output(port, GPIO.HIGH)


def lo(port):
    GPIO.output(port, GPIO.LOW)


def notification_signal(duration):
    hi(GOUT)
    time.sleep(duration)
    lo(GOUT)


signals = signals.Signals(notification_signal)


def onbutton_notification():
    th = threading.Thread(target=signals.ping)
    th.start()


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
        onbutton_notification()

def capture_fast(camera: PiCamera, stop_condition):
    camera.iso = 0
    camera.drc_strength = "off"
    camera.image_denoise = False

    for i, f in enumerate(camera.capture_continuous(TARGET + 'image-{timestamp:%Y.%m.%d-%H.%M.%S.%f}-burst.jpg', burst=True)):
        if stop_condition():
            break
        onbutton_notification()


button1 = Button()
button1.trigger = lambda: GPIO.input(GIN1)
button1.action = capture_quality

button2 = Button()
button2.trigger = lambda: GPIO.input(GIN2)
button2.action = capture_fast

buttons = [button1, button2]

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

# script start

# testing only
# def switch_button(butt, delay):
#     time.sleep(delay)   # delay before button
#     GPIO.set_mock_input(butt, 1)
#     time.sleep(2)
#     GPIO.set_mock_input(butt, 0)
#
# th = threading.Thread(target=switch_button, args=(9,4))
# th.start()
# th2 = threading.Thread(target=switch_button, args=(10, 8))
# th2.start()

with PiCamera() as cam:
    # main polling loop

    signals.welcome()

    while True:
        for button in buttons:
            if button.trigger():
                onbutton_notification()
                button.action(cam, lambda: not button.trigger())

            check_pendrive()

            time.sleep(0.1)