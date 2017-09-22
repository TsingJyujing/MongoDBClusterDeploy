import paramiko
import os
import time
from TestAPI import test_host
import re
import traceback

deploy_name = "ProcessManage"
deploy_path = "/root"


def walk_files(local_dir):
    all_files = list()

    if os.path.exists(local_dir):
        files = os.listdir(local_dir)
        for x in files:
            filename = os.path.join(local_dir, x)
            # isdir
            if os.path.isdir(filename):
                all_files.extend(walk_files(filename))
            else:
                all_files.append(filename)
    else:
        print('{} does not exist'.format(local_dir))
    return all_files

def upload_dir(ssh, sftp, local_dir, remote_dir):
    all_files = walk_files(local_dir)
    for x in all_files:
        filename = os.path.split(x)[-1]
        remote_file = os.path.split(x)[0].replace(local_dir, remote_dir,1)
        path = remote_file.replace('\\', '/')
        _ = ssh.exec_command('mkdir -p ' + path)
        remote_filename = path + '/' + filename
        sftp.put(x, remote_filename)
        print("Done transfer:  %s --> %s" % (x, remote_filename))

def get_sftp(host, username, password, port=22):
    t = paramiko.Transport((host, port))
    t.connect(username=username, password=password)
    return paramiko.SFTPClient.from_transport(t)


def get_ssh(host, username, password, port=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, 22, username=username, password=password, timeout=5)
    return client

def deploy_manage(host, port, username, password):
    sftp = get_sftp(host, username, password)
    ssh = get_ssh(host, username, password)
    try:
        # Kill python
        _, stdout, _ = ssh.exec_command("ps -aux|grep python")
        std_string = stdout.read().decode("UTF-8")
        print(std_string)
        pyprocs = [re.split("\s+", x) for x in std_string.split("\n")]
        for pyproc in filter(lambda x: len(x) > 3, pyprocs):
            pid = int(pyproc[1])
            if u"runserver" in pyproc and u"0.0.0.0:%d" % port in pyproc:
                print("Killing... process %d" % pid)
                ssh.exec_command("kill -s 9 %d" % pid)
        _, stdout, _ = ssh.exec_command("ps -aux|grep python")
        print(stdout.read().decode("UTF-8"))
        _ = ssh.exec_command("rm -rf " + os.path.join(deploy_path, deploy_name))

        # Upload new file
        upload_dir(ssh, sftp, "ProcessTrojan", os.path.join(deploy_path, deploy_name))

        # Run
        _ = ssh.exec_command("nohup python3 %s/manage.py runserver 0.0.0.0:%d >runserver.log &" % (deploy_name, port))
        _, stdout, _ = ssh.exec_command("ps -aux|grep python")
        print(stdout.read().decode("UTF-8"))
        time.sleep(5)
        # Test
        test_host(host, port)
        print("Done normally.")
    except Exception as ex:
        print("Some error happened in deploying.")
        print(traceback.format_exc())
    finally:
        ssh.close()
        sftp.close()


if __name__ == "__main__":
    # IP_list = ["172.16.9.81", "172.16.9.86", "172.16.9.87"]
    IP_list = ["172.16.9.95", "172.16.9.96"]
    for IP in IP_list:
        deploy_manage(IP, 10086, "root", "txj@618")
