# -*- coding: utf-8 -*-

from fridge import ThermalItem
from rand import RandomEvent
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

        self.splunkUrl = "10.97.0.104"
        self.splunkPort = 6666

    def sendToSplunk(self, thermalItems):
            response = self.ntpClient.request('3.us.pool.ntp.org')

            for i in self.thermalItems:
                data = "{\"timestamp\":\"%s\"," % ctime(response.tx_time)
                data += "\"Item\":\"%s\"," % (i.getName())
                data += "\"Temperature\":\"%s\"," % (i.getTemp())
                data += "\"isDoorOpen\":\"%s\"}" % (i.isDoorOpen())
                print data

                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.splunkUrl, self.splunkPort))
                client_socket.send(data)
                client_socket.close()

                i.tick()

    def simulate(self):
        while(1):
            if self.randEvent.openDoor():
                howLong = self.randEvent.howLong()
                index = self.randEvent.pickRandomItem(len(self.thermalItems))
                self.thermalItems[index].openDoor(howLong)

            self.sendToSplunk(self.thermalItems)

            time.sleep(1)

def main():
    items = []
    items.append(ThermalItem("Fridge1", 8))
    items.append(ThermalItem("Fridge2", 6))
    items.append(ThermalItem("Freezer1", -20))
    items.append(ThermalItem("Freezer2", -30))
    items.append(ThermalItem("Oven1", 250))
    items.append(ThermalItem("Oven2", 300))

    s = Simulator(items, roomTemp=20)
    s.simulate()

if __name__=="__main__":
    main()