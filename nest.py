#! /usr/bin/python

# nest.py -- a python interface to the Nest Thermostat
# by Scott M Baker, smbaker@gmail.com, http://www.smbaker.com/
#
# Usage:
#    'nest.py help' will tell you what to do and how to do it
#
# Licensing:
#    This is distributed unider the Creative Commons 3.0 Non-commecrial,
#    Attribution, Share-Alike license. You can use the code for noncommercial
#    purposes. You may NOT sell it. If you do use it, then you must make an
#    attribution to me (i.e. Include my name and thank me for the hours I spent
#    on this)
#
# Acknowledgements:
#    Chris Burris's Siri Nest Proxy was very helpful to learn the nest's
#       authentication and some bits of the protocol.

import time
import urllib
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import socket
import datetime
import sys
from threading import Thread, Lock
import subprocess

from optparse import OptionParser

try:
   import json
except ImportError:
   try:
       import simplejson as json
   except ImportError:
       print "No json library available. I recommend installing either python-json"
       print "or simpejson."
       sys.exit(-1)

class Nest:
    def __init__(self, username, password, serial=None, index=0, units="F"):
        self.username = username
        self.password = password
        self.serial = serial
        self.units = units
        self.index = index

    def loads(self, res):
        if hasattr(json, "loads"):
            res = json.loads(res.decode(encoding='ascii'), 'latin-1')
        else:
            res = json.read(res)
        return res

    def login(self):
        data = urllib.parse.urlencode({"username": self.username, "password": self.password})
        binary_data = data.encode("ascii")

        req = urllib2.Request("https://home.nest.com/user/login",
                              binary_data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4"})

        res = urllib2.urlopen(req).read()

        res = self.loads(res)

        self.transport_url = res["urls"]["transport_url"]
        self.access_token = res["access_token"]
        self.userid = res["userid"]

    def get_status(self):
        req = urllib2.Request(self.transport_url + "/v2/mobile/user." + self.userid,
                              headers={"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                                       "Authorization":"Basic " + self.access_token,
                                       "X-nl-user-id": self.userid,
                                       "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        res = self.loads(res)

        self.structure_id = list(res["structure"].keys())[0]

        if (self.serial is None):
            self.device_id = res["structure"][self.structure_id]["devices"][self.index]
            self.serial = self.device_id.split(".")[1]

        self.status = res

        #print "res.keys", res.keys()
        #print "res[structure][structure_id].keys", res["structure"][self.structure_id].keys()
        #print "res[device].keys", res["device"].keys()
        #print "res[device][serial].keys", res["device"][self.serial].keys()
        #print "res[shared][serial].keys", res["shared"][self.serial].keys()

    def temp_in(self, temp):
        if (self.units == "F"):
            return (temp - 32.0) / 1.8
        else:
            return temp

    def temp_out(self, temp):
        if (self.units == "F"):
            return temp*1.8 + 32.0
        else:
            return temp

    def show_status(self):
        shared = self.status["shared"][self.serial]
        device = self.status["device"][self.serial]

        allvars = shared
        allvars.update(device)

        for k in sorted(allvars.keys()):
             print(k + "."*(32-len(k)) + ":", allvars[k])

    def get_curtemp(self):
        return self.status["shared"][self.serial]["current_temperature"]

    def get_curhumid(self):
        return self.status["device"][self.serial]["current_humidity"]

    def show_curtemp(self):
        temp = self.status["shared"][self.serial]["current_temperature"]
        temp = self.temp_out(temp)

        print("%0.1f" % temp)

    def set_temperature(self, temp):
        temp = self.temp_in(temp)

        data = '{"target_change_pending":true,"target_temperature":' + '%0.1f' % temp + '}'
        req = urllib2.Request(self.transport_url + "/v2/put/shared." + self.serial,
                              data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                               "Authorization":"Basic " + self.access_token,
                               "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        print(res)

    def set_fan(self, state):
        data = '{"fan_mode":"' + str(state) + '"}'
        req = urllib2.Request(self.transport_url + "/v2/put/device." + self.serial,
                              data,
                              {"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                               "Authorization":"Basic " + self.access_token,
                               "X-nl-protocol-version": "1"})

        res = urllib2.urlopen(req).read()

        print(res)

def create_parser():
   parser = OptionParser(usage="nest [options] command [command_options] [command_args]",
        description="Commands: fan temp",
        version="unknown")

   parser.add_option("-u", "--user", dest="user",
                     help="username for nest.com", metavar="USER", default=None)

   parser.add_option("-p", "--password", dest="password",
                     help="password for nest.com", metavar="PASSWORD", default=None)

   parser.add_option("-c", "--celsius", dest="celsius", action="store_true", default=False,
                     help="use celsius instead of farenheit")

   parser.add_option("-s", "--serial", dest="serial", default=None,
                     help="optional, specify serial number of nest thermostat to talk to")

   parser.add_option("-i", "--index", dest="index", default=0, type="int",
                     help="optional, specify index number of nest to talk to")


   return parser


def sendData(splunkUrl, splunkPort, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((splunkUrl, splunkPort))
        client_socket.send(data)
        client_socket.close()
        print(data)

'''
def main():
    parser = create_parser()
    (opts, args) = parser.parse_args()

    units = "C"
    opts.user = "sangela.smoley@room5.com"
    opts.password = "IOTRoom5"
    splunkUrl = '10.97.0.252'
    #splunkUrl = "10.97.0.104"
    splunkPort = 8888
    prevTemp = 0
    prevHumid = 0

    n = Nest(opts.user, opts.password, opts.serial, opts.index, units=units)
    try:
        n.login()
        n.get_status()
    except:
        print "ERRROR login"

    loop = 0

    while(1):
        humid = n.status["device"][n.serial]["current_humidity"]
        temp =  n.status["shared"][n.serial]["current_temperature"]

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m/%d/%Y %H:%M:%S')
        data = "{\"timestamp\":\"%s\", \"id\":\"nest-sandiego\", \"temp\":\"%d\", \"humidity\":\"%d\"}\r\n" % (st, temp, humid)

        if prevTemp != temp or prevHumid != humid:
            sendData(splunkUrl, splunkPort, data)

        time.sleep(1)

        if loop >= (60):
            #sendData(splunkUrl, splunkPort, data)
            loop = 0

        loop = loop + 1
        prevTemp = temp
        prevHumid = humid


if __name__=="__main__":
   main()

'''
