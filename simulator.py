# -*- coding: utf-8 -*-

from fridge import ThermalItem
from rand import RandomEvent
from nest import Nest
import time
import ntplib
import socket
from time import ctime


class Simulator:

    def __init__(self, items, roomTemp=20):
        self.roomTemp = roomTemp
        self.thermalItems = items
        self.randEvent = RandomEvent()
        self.ntpClient = ntplib.NTPClient()

        self.splunkUrl = "192.168.0.10"
        self.splunkPort = 6666
        u = ""
        p = ""
        self.nest = Nest(u, p, serial=None, index=0, units="C")
        self.nest.login()

    def sendNestData(self):
        self.nest.get_status()

        humid = self.nest.status["device"][self.nest.serial]["current_humidity"]
        temp =  self.nest.status["shared"][self.nest.serial]["current_temperature"]

        data = "{\"timestamp\":\"%s\"," % self.getTime()
        data +=  "\"id\":\"%s\"," % ("StoreMart")
        data += "\"temperature\":\"%s\"," % (temp)
        data += "\"humidity\":\"%s\"}" % (humid)
        print data


    def getTime(self):
        while(1):
            try:
                ntpClient = ntplib.NTPClient()
                response = ntpClient.request('3.us.pool.ntp.org')
                return ctime(response.tx_time)
            except:
                pass

    def sendToSplunk(self):
            # Get data from Nest and send to splunk
            self.sendNestData()

            for i in self.thermalItems:
                data = "{\"timestamp\":\"%s\"," % self.getTime()
                data += "\"id\":\"%s\"," % (i.getName())
                data += "\"temperature\":\"%s\"," % (i.getTemp())
                if i.isDoorOpen():
                    data += "\"doorstatus\":\"OPENED\"}"
                else:
                    data += "\"doorstatus\":\"CLOSED\"}"
                print data

                #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #client_socket.connect((self.splunkUrl, self.splunkPort))
                #client_socket.send(data)
                #client_socket.close()

                # If the item is doorless simulate temp fluctuation
                if not i.hasItemDoor():
                    t = i.getInitTemp()
                    f = self.randEvent.fluctuation(t)
                    i.setTemp(f)
                i.tick()

    def simulate(self):
        while(1):
            # Pick one random thermalitem
            index = self.randEvent.pickRandomItem(len(self.thermalItems))
            thermalItem = self.thermalItems[index]
            # Did the door open
            if self.randEvent.openDoor():
                howLong = self.randEvent.howLong()
                if thermalItem.hasItemDoor():
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

    s = Simulator(items, roomTemp=20)
    s.simulate()

if __name__ == "__main__":
    main()