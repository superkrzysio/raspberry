import time
from threading import Thread

# my library of "signals" - rythms of HIGH signal associated with a name;
# most useful with vibrating engine or buzzer
class Signals:
    # a mini pause that separates 2 consecutive HIGH signals, so they are distinguishable
    PAUSE = 0.05

    # pass a method that will send the HIGH signal
    # method should accept one argument: duration of the signal
    def __init__(self, send):
        self.send = send

    def __pause(self, duration):
        time.sleep(duration)

    def __ring(self, duration):
        self.send(duration - self.PAUSE)
        time.sleep(self.PAUSE)

    def __call_me_later(self, method):
        Thread(target=method).start()

    def joy(self, asynch=False):
        if asynch:
            self.__call_me_later(self.joy)
            return
        self.__ring(0.2)
        self.__pause(0.2)
        self.__ring(0.2)
        self.__pause(0.4)

        self.__ring(0.2)
        self.__pause(0.2)
        self.__ring(0.2)
        self.__pause(0.4)

        self.__ring(0.2)
        self.__pause(0.2)
        self.__ring(0.2)
        self.__pause(0.8)


    def alert(self, asynch=False):
        if asynch:
            self.__call_me_later(self.alert)
            return
        for i in range(0, 10):
            self.__ring(0.4)
            self.__pause(0.4)

    def ping(self, asynch=False):
        if asynch:
            self.__call_me_later(self.ping)
            return
        self.__ring(0.2)

    def knock_knock(self, asynch=False):
        if asynch:
            self.__call_me_later(self.knock_knock)
            return
        self.__ring(0.2)
        self.__ring(0.2)
        self.__ring(0.2)
        self.__ring(0.2)
        self.__ring(0.2)

    def welcome(self, asynch=False):
        if asynch:
            self.__call_me_later(self.welcome)
            return
        self.__ring(0.2)
        self.__ring(0.6)

    def bye(self, asynch=False):
        if asynch:
            self.__call_me_later(self.bye)
            return
        self.__ring(1)
        self.__ring(0.2)
        self.__ring(0.2)

    def win(self, asynch=False):
        if asynch:
            self.__call_me_later(self.win)
            return
        self.knock_knock()  # todo
