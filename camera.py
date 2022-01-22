import os.path
import shutil

import RPi.GPIO as GPIO
import time
import threading
import signals

# script for taking photos with Raspberry with a button without preview
# uses 1 GPIO port for output signal (e.g. buzzer) and 1 for each button
# remember to power the buzzer through transistor; also see bug note below
# Use cases:
#   - ready to be started during OS boot
#   - press button1 to make photo in 1st configuration
#   - press button2 to make photo in 2nd configuration
#   - connect USB stick to automatically store all the photos on it, then dismount
#   - get vibration/sound confimations of all actions

# PS. strange bug I experienced:
# after connecting any loose wire to input port, it started blinking/fluctuating on/off - just without a reason
# also happened when I touched the port
# workaround: ground the port through 680k resistor


### constants
GIN1 = 9
GIN2 = 10
GOUT = 24
TARGET = "/home/pi/photos/"
PENDRIVE = "/usr/media/PENDRIVE/"    # usb storage partition label

# setup
if not os.path.exists(TARGET):
    os.mkdir(TARGET)

# gpio
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


def capture_quality():
    pass


def capture_fast():
    pass


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

    # dismount everything except /dev/sda - watch out
    drives = [sd for sd in os.listdir("/dev/") if sd.startswith("sd") and sd != "sda"]
    for drive in drives:
        os.system("umount /dev/" + drive)

    signals.win()

# script start

# main polling loop
while True:

    for button in buttons:
        if button.trigger():
            onbutton_notification()
            button.action()

        check_pendrive()

        time.sleep(0.1)