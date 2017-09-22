# -*- coding: utf-8 -*-
import time
import base64
import json
import hashlib
import yaml
from urllib import request, parse


def print_config(config_object, title=None):
    if title is not None:
        print(title)
    print(json.dumps(config_object, indent=4))





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



