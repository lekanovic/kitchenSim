# -*- coding: utf-8 -*-


class ThermalItem:
    def __init__(self, name, temp, roomTemp=20, coolingConstant=-0.07):
        self.name = name
        self.initTemp = self.temperature = temp
        self.doorOpen = False
        self.roomTemp = roomTemp
        self.k = coolingConstant
        self.time = 0

    def getName(self):
        return self.name

    def getTemp(self):
        return self.temperature

    def setTemp(self, temp):
        self.temperature = temp

    def isDoorOpen(self):
        if self.time > 0:
            return True
        return self.doorOpen

    def openDoor(self, sec=4):
        self.doorOpen = True
        self.time = sec

    def closeDoor(self):
        self.doorOpen = False

    def tick(self):
        if self.time > 0:
            self.time = self.time - 1
            self.temperature += (self.k * (self.temperature - self.roomTemp))
        else:
            self.closeDoor()
            self.temperature = self.initTemp

#http://rosettacode.org/wiki/Euler_method#Python
#def thermalbalance(item, k, roomTemp):
#    if item.isDoorOpen():
#        y = f3.getTemp()
#        y += (k * (y - roomTemp))
#        f3.setTemp(y)

#roomTemp = 20
#coolingConstant = -0.07
'''
f1 = ThermalItem("Fridge1", 8)
f2 = ThermalItem("Freezer1", -20)
f3 = ThermalItem("Oven1", 250)

f1.openDoor()
f3.openDoor()

for i in range(1,15):
    print "%s %s door open %s" % (f1.getName(), f1.getTemp(),f1.isDoorOpen())
    print "%s %s door open %s" % (f2.getName(), f2.getTemp(),f2.isDoorOpen())
    print "%s %s door open %s" % (f3.getName(), f3.getTemp(),f3.isDoorOpen())
    f1.tick()
    f2.tick()
    f3.tick()
'''

