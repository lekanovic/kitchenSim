# -*- coding: utf-8 -*-

import random


class RandomEvent:
    # d - number of times per day where the door is left open
    # o - number of times per day the doors is opened
    # 86400 - number of seconds per day
    def __init__(self, d=5, o=145):
        self.forgett_close_door = random.sample(range(1, 86400), d)
        self.times_door_opened = random.sample(range(1, 86400), o)

    def openDoor(self):
        rand = random.randrange(1, 86400)
        return rand in self.times_door_opened

    def howLong(self):
        rand = random.randrange(1, 86400)
        if rand in self.forgett_close_door:
            return (60 * 120)
        else:
            return random.randrange(3, 10)

    def pickRandomItem(self, totalItems):
        return random.randrange(0, totalItems)

r = RandomEvent()


'''
v = random.randrange(1, 86400)

a = random.sample(range(1, 86400), 3)

print v
print a

if v in a:
    print "hittade"
'''