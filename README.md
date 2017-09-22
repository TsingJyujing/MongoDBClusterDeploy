# MongoDBClusterDeploy

## Introduction
A deploy tool written in Python, can deploy mongoDB cluster simply.
Easy to use and easy to manage your cluster.

## Environment
This toolset may only deploy MongoDB cluster on linux machines, it based on python3, you may install dependencies of python:
```shell
sudo apt-get install python3-setuptools python3-pip
```
and install needed packages:
```
python3 -m pip install django paramiko psutil
```
And you should allow the port we use (you can indicate it by yourself and default is 10086) can pass the firewall.


## Deploy of manage tools
For managing process, you may deploy process manage utility first, and modify the code in `ProcessManager/AutoDeploy.py` to deploy manage tool on your cluster.

```python
if __name__ == "__main__":
    IP_list = ["172.16.9.81", "172.16.9.86", "172.16.9.87"]
    for IP in IP_list:
        deploy_manage(IP, your_port, "root", "your_root_passwd") # I have save passwd on my cluster so you may
```

The explaination of function `deploy_manage`：
```python
deploy_manage(Address of machine, manage port, ssh user,ssh passwd)
```

The deploy tool will auto-test the service after deploy it, if your machine start service slow than you image, the test will failed, but you can verify it manually:
`http://Address of machine:manage port/monitor/cpu`


## Copy MongoDB executable file
You may download your binaries on https://www.mongodb.com/, amd open `MongoDBClusterDeploy/setup_mongodb.py` modify:
```python
local_filepath = "mongodb-linux-x86_64-ubuntu1604-3.4.6/bin" # where your executable files located in
remote_location = "/usr/local/mongodb" # fix to you binaries where will located in your remote machine
```
And open`MongoDBClusterDeploy/config/machine.py` modify the variable `machine_list`
The explain of each unit：
```python
"m1": { # the name of the machine, should be unique
    "ip": "172.16.9.81", # Address
    "port": 22, # SSH port
    "user": "root", # SSH user
    "passwd": "txj@618", # SSH password
    "trojan":{
        "port":10086, # manager port
        "passwd":"b115Admin" # manager password, you may modify it in MongoDBClusterDeploy/ProcessManager/ProcessTrojan/ManageAPI/views.py key_list variable
    }
},
```
Then run `MongoDBClusterDeploy/setup_mongodb.py` to upload your files.

## Config and start your cluster
Open `MongoDBClusterDeploy/config/mongo.py` some variable you may modify:
```python
mongo_path = "/usr/local/mongodb/" # where your mongodb binaried located in
dbfile_path = "/media/data/mongodb" # where your data to storage
replset_oplog_size = 1024  # OPLOG size, megabyte
shard_service_pre_machine = [1, 1]  # The number of shards in eache repl set, each machine
```

To ensure `CLEANING_MODE = True` in `MongoDBClusterDeploy/remote_runner.py` if it is your first time to config your cluster。
Then run `MongoDBClusterDeploy/remote_runner.py` to config your cluster.

## The start and shutdown of MongoDB cluster
Use db.ShutdownServer() to shutdown your cluster.
If your're starting up cluster, modify `CLEANING_MODE = False` in `MongoDBClusterDeploy/remote_runner.py` and ensure the configures as same as you deploying.
Then run `MongoDBClusterDeploy/remote_runner.py` to config your cluster.

## Monitoring of MongoDB
TODO, run django project in `ClusterMonitor` can monitor mongoDB stat.