import time
import base64
import json
import hashlib
from urllib import request, parse


def get_key(passwd):
    salt = "%d" % int(time.time())
    return (salt, hashlib.sha224((passwd + salt).encode("UTF-8")).hexdigest())


def POST(url, data):
    req = request.Request(url, data=parse.urlencode(data).encode("UTF-8"), method="POST")
    return request.urlopen(req).read()


def GET(url, data):
    req = request.Request(url + "?" + parse.urlencode(data), method="GET")
    return request.urlopen(req).read()


def print_json(obj):
    print(json.dumps(obj, indent=4))


def print_reformat_json(json_str):
    print_json(json.loads(json_str))


def add_command(host, port, passwd, command):
    salt, key = get_key(passwd)
    return POST("http://%s:%d/process/create" % (host, port), {
        "cmd": base64.b64encode(command.encode("UTF-8")),
        "salt": salt,
        "key": key
    })


def kill_process(host, port, passwd, pid):
    salt, key = get_key(passwd)
    return POST("http://%s:%d/process/kill" % (host, port), {
        "pid": pid,
        "salt": salt,
        "key": key
    })


def list_processes(host, port, passwd):
    salt, key = get_key(passwd)
    return GET("http://%s:%d/process/list" % (host, port), {
        "salt": salt,
        "key": key
    })


def authentic_test(host, port, passwd):
    salt, key = get_key(passwd)
    return GET("http://%s:%d/authentic/test" % (host, port), {
        "salt": salt,
        "key": key
    })


def test_host(host, port):
    passwd = "b115Admin"
    auth_result = json.loads(authentic_test(host, port, passwd + "979323"))
    assert auth_result["status"] != "success", "Invalid key passed"
    auth_result = json.loads(authentic_test(host, port, passwd))
    assert auth_result["status"] == "success", "Valid key hasn't passed"
    json_obj = json.loads(add_command(host, port, passwd, "/bin/ping localhost"))
    print_json(json_obj)
    assert json_obj["status"]=="success", "Fail to append task."
    process_id = int(json_obj["pid"])
    time.sleep(1)
    print_reformat_json(list_processes(host,port,passwd))
    time.sleep(1)
    json_obj = kill_process(host,port,passwd,process_id)
    print_reformat_json(json_obj)
    print_reformat_json(list_processes(host,port,passwd))

