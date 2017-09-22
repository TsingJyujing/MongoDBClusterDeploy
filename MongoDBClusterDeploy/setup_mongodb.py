# -*- coding: utf-8 -*-
"""
将本地的MongoDB程序上传到服务器指定位置
"""
from util.Remote import RemoteConnection
from config.machine import machine_list

local_filepath = "mongodb-linux-x86_64-ubuntu1604-3.4.6/bin"
remote_location = "/usr/local/mongodb"


def main():
    for mk in machine_list.keys():
        machine = machine_list[mk]
        print("Setting up MongoDB in %s ..." % machine["ip"])
        rc = RemoteConnection(machine["ip"], machine["user"], machine["passwd"])
        rc.upload_dir(local_filepath, remote_location)
        rc.run_command("chmod 777 " + remote_location + "/*")
        rc.close()


if __name__ == "__main__":
    main()
