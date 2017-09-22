# -*- coding: utf-8 -*-
import time
import base64
import json
import hashlib
import yaml
from urllib import request, parse
import traceback

from django.http import HttpResponse


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


def get_prarmeter(req, key):
    try:
        return req.GET[key]
    except:
        return req.POST[key]


# noinspection PyBroadException
def get_GET_parameter(req, key, default_value):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return default value.
    :param req: request object created by django
    :param key: key
    :param default_value: default value
    :return:
    """
    try:
        return req.GET[key]
    except:
        return default_value


def get_POST_parameter(req, key, default_value):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return default value.
    :param req: request object created by django
    :param key: key
    :param default_value: default value
    :return:
    """
    try:
        return req.POST[key]
    except:
        return default_value


def get_json_response(obj):
    """
    Create a http response
    :param obj: object which json serializable
    :return:
    """
    return HttpResponse(json.dumps(obj))


def get_host(req):
    """
    Get host info from request META
    :param req:
    :return:
    """
    return req.META["HTTP_HOST"].split(":")[0]


def response_json_error_info(func):
    """
    Trying to run function, if exception caught, return error details with json format
    :param func:
    :return:
    """

    def wrapper(req):
        try:
            return func(req)
        except Exception as ex:
            return get_json_response({
                "status": "error",
                "error_info": str(ex),
                "trace_back": traceback.format_exc()
            })

    return wrapper


def response_json(func):
    """
    Trying to run function, if exception caught, return error details with json format, else return json formatted object
    :param func:
    :return:
    """

    def wrapper(req):
        try:

            return get_json_response(func(req))
        except Exception as ex:
            return get_json_response({
                "status": "error",
                "error_info": str(ex),
                "trace_back": traceback.format_exc()
            })

    return wrapper
