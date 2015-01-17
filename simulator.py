# -*- coding: utf-8 -*-

from fridge import ThermalItem
from rand import RandomEvent
from nest import Nest
import time
import ntplib
import socket
from time import ctime


class Simulator:

    def __init__(self, items):
        self.thermalItems = items
        self.randEvent = RandomEvent()
        self.ntpClient = ntplib.NTPClient()

        self.splunkUrl = "10.97.0.104"
        self.splunkPort = 6666

        u = ""
        p = ""
        self.nest = Nest(u, p, serial=None, index=0, units="C")
        self.nest.login()
        self.nest.get_status()
        self.roomTemp = self.nest.get_curtemp()

        for item in items:
            item.setRoomTemp(self.roomTemp)

    def sendNestData(self):
        self.nest.get_status()

        humid = self.nest.get_curhumid()
        temp = self.nest.get_curtemp()

        data = "{\"timestamp\":\"%s\"," % self.getTime()
        data += "\"id\":\"%s\"," % ("StoreMart")
        data += "\"temperature\":\"%s\"," % (temp)
        data += "\"humidity\":\"%s\"}" % (humid)

        self.sendTCP(data)

    def getTime(self):
        while(1):
            try:
                ntpClient = ntplib.NTPClient()
                response = ntpClient.request('3.us.pool.ntp.org')
                return ctime(response.tx_time)
            except:
                pass

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
        print data
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
            if i.isDoorOpen():
                data += "\"doorstatus\":\"OPENED\"}"
                status = True
            else:
                data += "\"doorstatus\":\"CLOSED\"}"

            self.sendTCP(data)

            # If the item is doorless simulate temp fluctuation
            if not i.hasItemDoor():
                t = i.getInitTemp()
                f = self.randEvent.fluctuation(t)
                i.setTemp(f)
            i.tick()
            if status and not i.isDoorOpen():
                status = False
                self.sendCloseDoorEvent(i)

    def simulate(self):
        while(1):
            # Pick one random thermalitem
            index = self.randEvent.pickRandomItem(len(self.thermalItems))
            thermalItem = self.thermalItems[index]
            # Did the door open
            if self.randEvent.openDoor():
                howLong = self.randEvent.howLong()
                if thermalItem.hasItemDoor():
                    self.sendOpenDoorEvent(thermalItem)
                    thermalItem.openDoor(howLong)

            self.sendToSplunk()

            #time.sleep(1)


def main():
    items = []
    items.append(ThermalItem("IceCream", -20))
    items.append(ThermalItem("Pizza", -30))
    items.append(ThermalItem("Vegetables", -20))
    items.append(ThermalItem("MilkandEggs", 4, hasDoor=False))
    items.append(ThermalItem("Cheese", 8, hasDoor=False))
    items.append(ThermalItem("Beer", 4))
    items.append(ThermalItem("Soda", 4))
    items.append(ThermalItem("HotWok", 300))

    s = Simulator(items)
    s.simulate()

if __name__ == "__main__":
    main()