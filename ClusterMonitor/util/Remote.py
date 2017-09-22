# -*- coding: utf-8 -*-
import base64
import hashlib
import os

import time
import yaml
import json
import paramiko

from util import POST, GET, print_reformat_json


class RemoteConnection:
    def __init__(self, host, username, password, port=22):
        self.connection = "ssl://%s@%s:%d/" % (username, host, port)
        print("Connecting %s" % self.connection)
        self.ssh_object = RemoteConnection.get_ssh(host, username, password, port)
        self.sftp_object = RemoteConnection.get_sftp(host, username, password, port)
        print("Connected to %s" % self.connection)

    def upload_dir(self, local_dir, remote_dir):
        all_files = RemoteConnection.__walk_files(local_dir)
        for x in all_files:
            filename = os.path.split(x)[-1]
            remote_file = os.path.split(x)[0].replace(local_dir, remote_dir, 1)
            path = remote_file.replace('\\', '/')
            _ = self.ssh_object.exec_command('mkdir -p ' + path)
            remote_filename = path + '/' + filename
            self.sftp_object.put(x, remote_filename)
            print("%s:  %s --> %s" % (self.connection, x, remote_filename))

    @classmethod
    def __walk_files(cls, local_dir):
        all_files = list()
        if os.path.exists(local_dir):
            files = os.listdir(local_dir)
            for x in files:
                filename = os.path.join(local_dir, x)
                if os.path.isdir(filename):
                    all_files.extend(RemoteConnection.__walk_files(filename))
                else:
                    all_files.append(filename)
        else:
            print('{} does not exist'.format(local_dir))
        return all_files

    @classmethod
    def get_sftp(cls, host, username, password, port=22):
        t = paramiko.Transport((host, port))
        t.connect(username=username, password=password)
        return paramiko.SFTPClient.from_transport(t)

    @classmethod
    def get_ssh(cls, host, username, password, port=22):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, 22, username=username, password=password, timeout=5)
        return client

    def write_file(self, filename, filetext):
        with self.sftp_object.file(filename, "wb") as rmfp:
            rmfp.write(filetext)

    def write_json(self, filename, object, encode_format="UTF-8"):
        self.write_file(filename, json.dumps(object).encode(encode_format))

    def write_yaml(self, filename, object):
        self.write_file(filename, yaml.dump(object))

    def run_command(self, command):
        _ = self.ssh_object.exec_command(command)

    def close(self):
        self.ssh_object.close()
        self.sftp_object.close()
        print("Closed: %s" % self.connection)


def get_key(passwd):
    salt = "%d" % int(time.time())
    return (salt, hashlib.sha224((passwd + salt).encode("UTF-8")).hexdigest())


def run_command(host, port, passwd, command):
    print("Starting command at %s:%s" % (host, command))
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


def clean_process(host, port, passwd):
    processes = json.loads(list_processes(host, port, passwd))
    for process in processes:
        print("Killing: %d" % process["pid"])
        print_reformat_json(kill_process(host, port, passwd, process["pid"]))


def get_cpu_status(host, port):
    return json.loads(GET("http://%s:%d/monitor/cpu" % (host, port), {"interval": 1}))


def get_memory_status(host, port):
    return json.loads(GET("http://%s:%d/monitor/memory" % (host, port), {}))


def get_network_status(host, port):
    return json.loads(GET("http://%s:%d/monitor/network" % (host, port), {}))
