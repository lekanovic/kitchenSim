# -*- coding: utf-8 -*-

import random


class RandomEvent:
    # d - number of times per day where the door is left open
    # o - number of times per day the doors is opened
    # 86400 - number of seconds per day
    def __init__(self, d=5, o=145):
        self.forgett_close_door = d
        self.times_door_opened = o

    def openDoor(self):
        rand = random.randrange(1, 86400)
        return rand <= self.times_door_opened

    def howLong(self):
        rand = random.randrange(1, 86400)
        # Sometimes the door is forgotten to be closed
        # Then have it open random from 1h to 10h
        if rand <= self.forgett_close_door:
            return random.randrange(60 * 60, 60 * 60 * 10)
        else:
            return random.randrange(3, 10)

    def pickRandomItem(self, thermalItems):
        index = random.randrange(0, len(thermalItems))
        return thermalItems[index]

    def fluctuation(self, v):
        return random.randrange(v - 1, v + 2)

    def shallWeTurnOn(self):
        rand = random.randrange(1, 86400)
        return rand <= 250

    def shallWeTurnOff(self):
        rand = random.randrange(1, 10)
        return rand <= 2

r = RandomEvent()
