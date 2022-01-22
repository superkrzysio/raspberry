import time

# my library of "signals" - rythms of HIGH signal associated with a name;
# most useful with vibrating engine or buzzer
# possible TODO: async mode
class Signals:
    # a mini pause that separates 2 consecutive HIGH signals, so they are distinguishable
    PAUSE = 0.05

    # pass a method that will send the HIGH signal
    # method should accept one argument: duration of the signal
    def __init__(self, send):
        self.send = send

    def pause(self, duration):
        time.sleep(duration)

    def ring(self, duration):
        self.send(duration - self.PAUSE)
        time.sleep(self.PAUSE)

    def joy(self):
        self.ring(0.2)
        self.pause(0.2)
        self.ring(0.2)
        self.pause(0.4)

        self.ring(0.2)
        self.pause(0.2)
        self.ring(0.2)
        self.pause(0.4)

        self.ring(0.2)
        self.pause(0.2)
        self.ring(0.2)
        self.pause(0.8)

    def alert(self):
        for i in range(0, 10):
            self.ring(0.4)
            self.pause(0.4)

    def ping(self):
        self.ring(0.2)

    def knock_knock(self):
        self.ring(0.2)
        self.ring(0.2)
        self.ring(0.2)
        self.ring(0.2)
        self.ring(0.2)

    def welcome(self):
        self.ring(0.2)
        self.ring(0.6)

    def win(self):
        self.knock_knock()  # todo