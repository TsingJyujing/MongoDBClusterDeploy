# -*- coding: utf-8 -*-

"""
Yuan Yifan created in 2017-9-12 17:34:30
"""
from config.mongo import *
from config.machine import machine_list
from util import *
from util.Remote import RemoteConnection, run_command, clean_process
from os.path import join as raw_join
from config import templates
import pymongo
import traceback

CLEANING_MODE = True
REMOTE_CONTROL_PASSWD = "979323846"
REMOTE_CONTROL_PORT = 10086


def join(path, *paths):
    return raw_join(path, *paths).replace("\\", "/")


connection_dict = {mk: RemoteConnection(
    machine_list[mk]["ip"],
    machine_list[mk]["user"],
    machine_list[mk]["passwd"],
    machine_list[mk]["port"]
) for mk in machine_list.keys()}


def close_connections():
    for mk in machine_list.keys():
        connection_dict[mk].close()


def clean_path():
    for mk in connection_dict.keys():
        connection_dict[mk].run_command("rm -rf %s" % dbfile_path)
        connection_dict[mk].run_command("mkdir -p %s" % log_path)
        connection_dict[mk].run_command("mkdir -p %s" % conf_path)
        connection_dict[mk].run_command("mkdir -p %s" % data_path)


def generate_configsvr(machine_key):
    """
    生成配置服务器集群所需要的配置文件，并且给出启动命令
    :param machine_key:
    :return:
    """
    conn = connection_dict[machine_key]
    yaml_saving_path = join(conf_path, "configsvr.yaml")
    configsvr_data_path = join(data_path, "configsvr")
    conn.run_command("mkdir -p " + configsvr_data_path)
    if CLEANING_MODE:
        config_config = templates.configure_file_model
        config_config["replication"] = {
            "oplogSizeMB": int(replset_oplog_size / 10),
            "replSetName": configsvr_replSetName,
            "enableMajorityReadConcern": True
        }
        config_config["systemLog"]["path"] = join(log_path, "configsvr.log")
        config_config["net"]["port"] = configsvr_port
        config_config["storage"]["dbPath"] = configsvr_data_path
        config_config["sharding"]["clusterRole"] = "configsvr"
        conn.write_yaml(yaml_saving_path, config_config)
    return "%s --config %s" % (mongod_path, yaml_saving_path)


def set_configsvr_cluster():
    """
    配置MongoDB配置服务器集群
    :return:
    """
    machine = machine_list[machine_list.keys().__iter__().__next__()]
    pyconn = pymongo.MongoClient(machine["ip"], configsvr_port)
    admin_db = pyconn.get_database("admin")
    config_object = {
        "_id": configsvr_replSetName,
        "members": [{
            "_id": index,
            "host": "%s:%d" % (machine_list[mk]["ip"], configsvr_port)
        } for index, mk in enumerate(machine_list.keys())]
    }
    set_result = admin_db.command("replSetInitiate", config_object)
    if set_result["ok"] != 1.0:
        print("Warning: set configure cluster failed.")
    pyconn.close()


def generate_shardsvr(machine_key, replset_id, shard_id):
    conn = connection_dict[machine_key]
    shading_data_path = join(data_path, "shard_%d_%d" % (replset_id, shard_id))
    conn.run_command("mkdir -p " + shading_data_path)
    shading_log_file = join(log_path, "shard_%d_%d.log" % (replset_id, shard_id))
    yaml_saving_path = join(conf_path, "shard_%d_%d.yaml" % (replset_id, shard_id))
    shading_port = shard_port_start + replset_id * 10 + shard_id
    replset_name = "replset_%d" % replset_id
    if CLEANING_MODE:
        shading_config = templates.configure_file_model
        shading_config["replication"] = {
            "oplogSizeMB": replset_oplog_size,
            "replSetName": replset_name,
            "enableMajorityReadConcern": True
        }
        shading_config["systemLog"]["path"] = shading_log_file
        shading_config["net"]["port"] = shading_port
        shading_config["storage"]["dbPath"] = shading_data_path
        shading_config["sharding"]["clusterRole"] = "shardsvr"
        conn.write_yaml(yaml_saving_path, shading_config)
    return "%s --config %s" % (mongod_path, yaml_saving_path)


def set_shardsvr_cluster(replset_id):
    """
    配置MongoDB分片服务器集群
    :return:
    """
    machine = machine_list[machine_list.keys().__iter__().__next__()]
    members = []
    t = 0
    for mk, mac in machine_list.items():
        for i in range(shard_service_pre_machine[replset_id]):
            port = shard_port_start + replset_id * 10 + i
            members.append({
                "_id": t,
                "host": "%s:%d" % (mac["ip"], port)
            })
            t += 1

    pyconn = pymongo.MongoClient(machine["ip"], shard_port_start + replset_id * 10)
    admin_db = pyconn.get_database("admin")
    config_object = {
        "_id": "replset_%d" % replset_id,
        "members": members
    }
    set_result = admin_db.command("replSetInitiate", config_object)
    if set_result["ok"] != 1.0:
        print("Warning: set replset %d cluster failed." % replset_id)
    pyconn.close()


def generate_routesvr(machine_key):
    conn = connection_dict[machine_key]
    yaml_saving_path = join(conf_path, "route.yaml")
    if CLEANING_MODE:
        router_config = templates.router_configure_file_model
        router_config["net"]["port"] = route_port_start
        router_config["systemLog"]["path"] = join(log_path, "route.log")
        router_config["sharding"] = {
            "configDB": configsvr_replSetName + "/" + ",".join([
                "%s:%d" % (machine_list[mk]["ip"], configsvr_port)
                for mk in machine_list.keys()
            ])
        }
        conn.write_yaml(yaml_saving_path, router_config)
    return "%s --config %s" % (mongos_path, yaml_saving_path)


def set_routesvr():
    machine = machine_list[machine_list.keys().__iter__().__next__()]
    router_entry = pymongo.MongoClient(machine["ip"], route_port_start)
    admin_db = router_entry.get_database("admin")
    for replset_id in range(replset_count):
        replset_name = "replset_%d" % replset_id
        service_list = []
        for mk in connection_dict.keys():
            ip = machine_list[mk]["ip"]
            for shard_id in range(shard_service_pre_machine[replset_id]):
                port = shard_port_start + replset_id * 10 + shard_id
                service_list.append("%s:%d" % (ip, port))
        shard_info = replset_name + "/" + ",".join(service_list)
        result = admin_db.command("addShard", shard_info)
        print("路由服务器配置中...")
        print("副本集增加结果:" + shard_info + "结果")
        print_json(result)


def kill_all_process():
    for mk in connection_dict.keys():
        clean_process(machine_list[mk]["ip"], REMOTE_CONTROL_PORT, REMOTE_CONTROL_PASSWD)


def main():
    if CLEANING_MODE:
        clean_path()
    kill_all_process()
    for replset_id in range(replset_count):
        print("正在启动分片%d" % replset_id)
        for mk in connection_dict.keys():
            for shard_id in range(shard_service_pre_machine[replset_id]):
                cmd = generate_shardsvr(mk, replset_id, shard_id)
                result = run_command(machine_list[mk]["ip"], REMOTE_CONTROL_PORT, REMOTE_CONTROL_PASSWD, cmd)
                print("服务器 %s MongoDB Shard Server %d-%d 启动结果：" % (machine_list[mk]["ip"], replset_id, shard_id))
                print_reformat_json(result)
        time.sleep(5)
        if CLEANING_MODE:
            set_shardsvr_cluster(replset_id)

    print("正在为远程服务器集群生成配置文件...")
    start_configsvr_commands = {mk: generate_configsvr(mk) for mk in connection_dict.keys()}
    for mk, cmd in start_configsvr_commands.items():
        result = run_command(machine_list[mk]["ip"], REMOTE_CONTROL_PORT, REMOTE_CONTROL_PASSWD, cmd)
        print("服务器 %s MongoDB Config Server 启动结果：" % machine_list[mk]["ip"])
        print_reformat_json(result)
    time.sleep(5)
    if CLEANING_MODE:
        set_configsvr_cluster()

    print("正在配置路由服务器们...")
    for mk in connection_dict.keys():
        result = run_command(machine_list[mk]["ip"], REMOTE_CONTROL_PORT, REMOTE_CONTROL_PASSWD, generate_routesvr(mk))
        print("服务器 %s MongoDB Route Server 启动结果：" % machine_list[mk]["ip"])
        print_reformat_json(result)
    time.sleep(5)
    set_routesvr()

    print("全部配置结束")


if __name__ == "__main__":
    try:
        main()
    except:
        print(traceback.format_exc())
    finally:
        close_connections()
