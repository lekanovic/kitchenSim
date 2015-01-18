# -*- coding: utf-8 -*-


class Stove:

    def __init__(self, name, roomTemp=20):
        self.name = name
        self.maxTemp = 350
        self.isOn = False
        self.temperature = 15
        self.k = -0.07
        self.roomTemp = roomTemp
        self.onTime = 0

    def setRoomTemp(self, temp):
        self.rooTemp = temp

    def setTemp(self, temp):
        self.temperature = temp

    def getName(self):
        return self.name

    def getTemp(self):
        return self.temperature

    def isTurnedOn(self):
        return self.isOn

    def timeStoveHasBeenOn(self):
        return self.onTime

    def turnOn(self):
        self.isOn = True
        self.onTime = 0

    def turnOff(self):
        self.isOn = False

    def tick(self):
        if self.isOn and self.temperature <= self.maxTemp:
            self.temperature += self.temperature * 0.16
            self.onTime = self.onTime + 1
            if self.temperature > self.maxTemp:
                self.temperature = self.maxTemp
        elif not self.isOn and self.temperature >= self.roomTemp:
            self.temperature += (self.k * (self.temperature - self.roomTemp))


class ThermalItem:
    def __init__(self, name, temp, roomTemp=20, coolingConstant=-0.07, hasDoor=True):
        self.name = name
        self.initTemp = self.temperature = temp
        self.doorOpen = False
        self.roomTemp = roomTemp
        self.k = coolingConstant
        self.time = 0
        self.hasDoor = hasDoor
        self.timeDoorIsOpen = 0
        self.closeEvent = False

    def getInitTemp(self):
        return self.initTemp

    def getName(self):
        return self.name

    def getTemp(self):
        return self.temperature

    def setTemp(self, temp):
        self.temperature = temp

    def setRoomTemp(self, temp):
        self.temperature = temp

    def hasItemDoor(self):
        return self.hasDoor

    def isDoorOpen(self):
        if not self.hasDoor:
            return True
        if self.time > 0:
            return True
        return self.doorOpen

    def openDoor(self, sec=4):
        if self.doorOpen:
            return
        self.doorOpen = True
        self.time = self.timeDoorIsOpen = sec

    def closeDoor(self):
        self.doorOpen = False

    def howLongHasdoorBeenOpen(self):
        return self.timeDoorIsOpen

    def tick(self):
        # If the Item has no door return
        if not self.hasDoor:
            return

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
f2 = ThermalItem("Freezer1", -20,hasDoor=False)
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


f1 = Stove("HotWook")
print "Turn on"
f1.turnOn()

for i in range(1,25):
    print f1.getTemp()
    f1.tick()

print "Turn off"
f1.turnOff()

for i in range(1,25):
    print f1.getTemp()
    f1.tick()


print "Turn on"
f1.turnOn()

for i in range(1,25):
    print f1.getTemp()
    f1.tick()

'''