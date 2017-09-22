# -*- coding: utf-8 -*-
"""
基础配置文件，配置Mongo环境参数、端口参数和存储位置参数
"""
import os
from .machine import machine_list

mongo_path = "/usr/local/mongodb/"
mongod_path = os.path.join(mongo_path, "mongod")
mongos_path = os.path.join(mongo_path, "mongos")

dbfile_path = "/media/data/mongodb"

configsvr_port= 27100
configsvr_replSetName = "configure_cluster"

route_port_start = 27017
shard_port_start = 27300

project_prefix = "HistoricalGPS"
replset_prefix = "shard"  # 副本集ID前缀
replset_oplog_size = 1024  # OPLOG大小，单位Mb

ip_list = [machine_list[mk]["ip"] for mk in machine_list.keys()]
if "localhost" in ip_list or "127.0.0.1" in ip_list:
    print("警告：本地IP或者localhost不应在非测试环境使用")

machine_count = len(ip_list)  # 副本集数量

shard_service_pre_machine = [2, 2]  # 每台机器的各个副本集的分片数量
replset_count = len(shard_service_pre_machine)  # 副本集分片配置

assert len(ip_list) >= 3, "非实验环境不推荐少于2台机器的集群配置"
for val in shard_service_pre_machine:
    assert val < 10, "单机分片不应该超过10个（除非电脑性能好到爆炸）"
assert replset_count < 10, "冗余备份不推荐超过10份（多活也不能这么玩啊喂）"

log_path = os.path.join(dbfile_path, "log").replace("\\","/")
conf_path = os.path.join(dbfile_path, "conf").replace("\\","/")
data_path = os.path.join(dbfile_path, "db").replace("\\","/")

