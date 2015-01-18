# -*- coding: utf-8 -*-

from fridge import ThermalItem
from fridge import Stove
from rand import RandomEvent
from nest import Nest
import cProfile
import time
import datetime
import ntplib
import socket
from time import ctime
import sys

using_fake_nest = False
default_room_temp = 20
default_room_humidity = 40

class Simulator:

    def __init__(self, items, nest_login, nest_password):
        global using_fake_nest
        self.thermalItems = items
        self.randEvent = RandomEvent()
        self.ntpClient = ntplib.NTPClient()

        self.splunkUrl = "192.168.0.10"
        self.splunkPort = 5555

        if nest_login != "":
            using_fake_nest = False;
            u = nest_login
            p = nest_password
            self.nest = Nest(u, p, serial=None, index=0, units="C")
            self.nest.login()
            self.nest.get_status()
            self.roomTemp = self.nest.get_curtemp()
        else:
            using_fake_nest = True
            self.roomTemp = default_room_temp;

        for item in items:
            item.setRoomTemp(self.roomTemp)

    def sendNestData(self):
        global using_fake_nest
        humid = default_room_humidity
        temp = default_room_temp
        if using_fake_nest == False:
            self.nest.get_status()
            humid = self.nest.get_curhumid()
            temp = self.nest.get_curtemp()

        data = "{\"timestamp\":\"%s\"," % self.getTime()
        data += "\"id\":\"%s\"," % ("StoreMart")
        data += "\"temperature\":\"%s\"," % (temp)
        data += "\"humidity\":\"%s\"}" % (humid)

        self.sendTCP(data)

    def getTime(self):
        return  self.curTime.strftime("%c")

    def sendOpenDoorEvent(self, item):
        data = "{\"timestamp\":\"%s\"," % self.getTime()
        data += "\"id\":\"%s\"," % (item.getName())
        data += "\"doorevent\":\"OPENED\"}"
        self.sendTCP(data)

    def sendCloseDoorEvent(self, item):
        data = "{\"timestamp\":\"%s\"," % self.getTime()
        data += "\"id\":\"%s\"," % (item.getName())
        data += "\"doorevent\":\"CLOSED\","
        data += "\"openlength\":\"%s\"}" % (item.howLongHasdoorBeenOpen())
        self.sendTCP(data)

    def sendTCP(self, data):
        print(data)
        return
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.splunkUrl, self.splunkPort))
        client_socket.send(data)
        client_socket.close()

    def sendToSplunk(self):
        # Get data from Nest and send to splunk
        self.sendNestData()

        for i in self.thermalItems:
            status = False
            data = "{\"timestamp\":\"%s\"," % self.getTime()
            data += "\"id\":\"%s\"," % (i.getName())
            data += "\"temperature\":\"%s\"," % (i.getTemp())

            if not isinstance(i, Stove) and i.isDoorOpen():
                data += "\"doorstatus\":\"OPENED\"}"
                status = True
            else:
                data += "\"doorstatus\":\"CLOSED\"}"

            self.sendTCP(data)

            # If the item is doorless simulate temp fluctuation
            if not isinstance(i, Stove) and not i.hasItemDoor():
                t = i.getInitTemp()
                f = self.randEvent.fluctuation(t)
                i.setTemp(f)

            if isinstance(i, Stove):
                self.simulateStove(i)

            i.tick()
            if not isinstance(i, Stove) and status and not i.isDoorOpen():
                status = False
                self.sendCloseDoorEvent(i)

    def simulateStove(self, s):
        if not s.isTurnedOn() and self.randEvent.shallWeTurnOn():
            s.turnOn()
        elif s.timeStoveHasBeenOn() > (60 * 20) and self.randEvent.shallWeTurnOff():
            s.turnOff()

    def simulate(self):
        x = ntplib.NTPClient()
        self.curTime = datetime.datetime.utcfromtimestamp(x.request('europe.pool.ntp.org').tx_time)

        for i in range(0, 10000):
            # Pick one random thermalitem
            thermalItem = self.randEvent.pickRandomItem(self.thermalItems)
            # Did the door open
            if not isinstance(thermalItem, Stove) and self.randEvent.openDoor():
                howLong = self.randEvent.howLong()
                if thermalItem.hasItemDoor():
                    self.sendOpenDoorEvent(thermalItem)
                    thermalItem.openDoor(howLong)

            self.sendToSplunk()
            self.curTime = self.curTime + datetime.timedelta(0, 1)

            #time.sleep(1)


def main():
    nest_login = ""
    nest_password = ""

    #Get Nest login info from commandline
    if len(sys.argv) > 1:
        nest_login = str(sys.argv[1])
        nest_password = str(sys.argv[2])

    items = []
    items.append(ThermalItem("Ice Cream", -20))
    items.append(ThermalItem("Frozen Pizza", -30))
    items.append(ThermalItem("Frozen Veg", -20))
    items.append(ThermalItem("Milk and Eggs", 4, hasDoor=False))
    items.append(ThermalItem("Cheese", 8, hasDoor=False))
    items.append(ThermalItem("Beer", 4))
    items.append(ThermalItem("Soda", 4))
    items.append(Stove("HotWok"))

    s = Simulator(items, nest_login, nest_password)
    s.simulate()
    #cProfile.runctx('s.simulate()',globals(),locals())

if __name__ == "__main__":
    main()