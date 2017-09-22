# -*- coding: utf-8 -*-

# 配置模板
configure_file_model = {
    # 日志配置
    "systemLog": {
        "verbosity": 0,  # 日志输出的详细等级，从0~5越来越详细
        "quiet": False,  # 是否安静模式，一般不要使用，DEBUG的时候会想死
        "traceAllExceptions": False,  # 你打出来我也不一定看的懂
        "path": None,  # 日志的位置，待定
        "destination": "file"  # 日志输出到文件
    },
    # 网络配置
    "net": {
        "bindIp": "0.0.0.0",
        "port": None,  # 端口号 待配置
        "http": {
            "enabled": True,
            "RESTInterfaceEnabled": True
        },
    },
    # 其它参数配置
    "setParameter": {
        "enableLocalhostAuthBypass": False
    },
    "sharding": {
        "clusterRole": None
    },
    # 存储配置
    "storage": {
        "dbPath": None,
        "directoryPerDB": True,  # 每个数据库一个文件夹，小爷我喜欢
        "syncPeriodSecs": 120,  # 120秒同步一次
        "engine": "wiredTiger",
        "wiredTiger": {  # 当然要用“有线老虎”引擎啦~
            "engineConfig": {
                "cacheSizeGB": 1,  # 最大的Cache大小，看菜吃饭
            }
        }
    }
}

# 配置模板
router_configure_file_model = {
    # 日志配置
    "systemLog": {
        "verbosity": 0,  # 日志输出的详细等级，从0~5越来越详细
        "quiet": False,  # 是否安静模式，一般不要使用，DEBUG的时候会想死
        "traceAllExceptions": False,  # 你打出来我也不一定看的懂
        "path": None,  # 日志的位置，待定
        "destination": "file"  # 日志输出到文件
    },
    # 网络配置
    "net": {
        "bindIp": "0.0.0.0",
        "port": None,  # 端口号 待配置
    },
    # 其它参数配置
    "setParameter": {
        "enableLocalhostAuthBypass": False
    }
}
