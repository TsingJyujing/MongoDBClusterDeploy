from urllib import parse, request

from django.shortcuts import render

# Create your views here.
from config.machine import machine_list
from util.Remote import *
from util import response_json
import threading


class GETThread(threading.Thread):
    def __init__(self, url, data={}):
        threading.Thread.__init__(self)
        self.url = url
        self.data = data

    def run(self):
        req = request.Request(self.url + "?" + parse.urlencode(self.data), method="GET")
        self.data = request.urlopen(req).read()


class GetServerStatusThread(threading.Thread):
    def __init__(self, machine_info):
        threading.Thread.__init__(self)
        self.machine = machine_info

    def run(self):
        host = self.machine["ip"]
        port = self.machine["trojan"]["port"]

        cpuThread = GETThread("http://%s:%d/monitor/cpu" % (host, port))
        cpuThread.start()

        networkThread = GETThread("http://%s:%d/monitor/network" % (host, port))
        networkThread.start()

        memoryThread = GETThread("http://%s:%d/monitor/memory" % (host, port))
        memoryThread.start()

        cpuThread.join()
        networkThread.join()
        memoryThread.join()
        try:
            self.data = {
                "ip": host,
                "cpu": json.loads(cpuThread.data)["cpu"],
                "memory": json.loads(memoryThread.data)["memory"],
                "network": json.loads(networkThread.data)["network"],
            }
        except:
            self.data = None


@response_json
def get_cluster_status(req):
    threadList = [GetServerStatusThread(machine_list[mk]) for mk in machine_list]
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()
    return [
        thread.data for thread in threadList if thread.data is not None
    ]
