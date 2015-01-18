# -*- coding: utf-8 -*-

import random


class RandomEvent:

    def __init__(self):
        pass

    def openDoor(self):
        return random.randrange(1, 50) == 1

    def howLong(self):
        rand = random.randrange(1, 550)
        # Sometimes the door is forgotten to be closed
        # Then have it open random from 1h to 10h
        if rand <= 1:
            return random.randrange(60 * 5, 60 * 10)
        else:
            return random.randrange(3, 10)

    def pickRandomItem(self, thermalItems):
        index = random.randrange(0, len(thermalItems))
        return thermalItems[index]

    def fluctuation(self, v):
        return random.randrange(v - 1, v + 2)

    def shallWeTurnOn(self):
        return random.randrange(1, 250) == 1

    def shallWeTurnOff(self):
        return random.randrange(1, 10) == 1

r = RandomEvent()
