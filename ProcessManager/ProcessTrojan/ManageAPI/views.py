import string

import time
import subprocess
import psutil
import base64
import hashlib

from django.views.decorators.csrf import csrf_exempt

import Utility
from Utility import response_json

process_set = set()
warning_list = list()

key_list = (u"super_user_+1s",u'b115Admin')
salt_expired = 5 * 60
need_authentic = False


class ManagedProcess:
    def __init__(self, command, alias="process"):
        self.command = command
        self.alias = alias
        self.pobj = subprocess.Popen(command.split(" "))
        print("Process started normally.")

    @property
    def pid(self):
        return self.pobj.pid

    def kill(self):
        self.pobj.kill()
        return self.pobj.returncode


# Append subprocess
@csrf_exempt
@response_json
def append_process(request):
    if need_authentic:
        auth_request(request)
    command_line = base64.b64decode(request.POST["cmd"]).decode("UTF-8")
    alias = Utility.get_POST_parameter(request, "alias", "Alias")
    process_object = ManagedProcess(command_line, alias)
    process_set.add(process_object)
    return {
        "status": "success",
        "pid": process_object.pid
    }


# Kill(remove) subprocess
@csrf_exempt
@response_json
def kill_process(request):
    if need_authentic:
        auth_request(request)
    pid = int(request.POST["pid"])
    for process in process_set:
        if int(process.pid) == pid:
            process_set.remove(process)
            return {
                "status": "success",
                "returncode": process.kill()
            }
    else:
        raise Exception("Process not found by given PID:%d" % pid)


# List subprocess
@response_json
def list_process(request):
    if need_authentic:
        auth_request(request)
    return [{
        "pid": process.pid,
        "alias": process.alias,
        "command": process.command,
        "mem": psutil.Process(process.pid).memory_info()
    } for process in process_set]


@response_json
def get_cpu_stat(request):
    interval = float(Utility.get_GET_parameter(request, "interval", "0.5"))
    return {
        "status": "success",
        "cpu": psutil.cpu_percent(interval, True)
    }


@response_json
def get_memory(request):
    vmem_info = psutil.virtual_memory()
    smem_info = psutil.swap_memory()
    return {
        "status": "success",
        "memory": {
            "virtual": {
                "total": vmem_info.total,
                "used": vmem_info.used
            },
            "swap": {
                "total": smem_info.total,
                "used": smem_info.used
            }
        }
    }


@response_json
def get_net_io(request):
    net_info = psutil.net_io_counters()
    return {
        "status": "success",
        "network": {
            "bytes": {
                "sent": net_info.bytes_sent,
                "received": net_info.bytes_recv
            },
            "packets": {
                "sent": net_info.packets_sent,
                "received": net_info.packets_recv
            },
            "error": {
                "in": net_info.errin,
                "out": net_info.errout
            },
            "drop": {
                "in": net_info.dropin,
                "out": net_info.dropout
            }
        }
    }


@response_json
def authentic_test(request):
    auth_request(request)
    return {"status": "success"}


def auth_request(requset):
    key_input = Utility.get_prarmeter(requset, "key")
    salt = Utility.get_prarmeter(requset, "salt")
    tick = int(salt)
    assert abs(int(time.time()) - tick) < salt_expired, "Key expired."
    for key in key_list:
        if hashlib.sha224((key + salt).encode()).hexdigest() == key_input:
            return True
    else:
        raise Exception("Authentic failed caused by key not found")
