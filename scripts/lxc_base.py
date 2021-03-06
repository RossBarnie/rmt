# Script to start an LXC container, assumes dependencies resolved
import command
import string
import psutil
import os
import sys
import container_usage

# need root access to start containers

__containers = []
__euid = os.geteuid()  # integer


def __get_containers():
    global __containers
    com_out = command.Command(["lxc-ls"]).execute(return_output=True)
    if com_out.get("comm_retval") is not None:
        __containers = com_out.get("comm_retval")
        __containers = __containers.splitlines()
    else:
        print "Error retrieving container list, emptying container list"
        __containers = []


def __get_pid_from_lxc_info(container_name):
    com = command.Command(["lxc-info", "-n", container_name]).execute(True)
    info = com["comm_retval"]
    return info.split("\n")[1].split()[1]


def root_access():
    return __euid == 0


def __start(cmd_dict):
    # cmd_dict has:
    #     cmd_list: list representation of command
    #     container_name: name of container

    res = False

    if not check_input(cmd_dict["container_name"]):
        print "Invalid input\n"
        return res

    if not root_access():
        print "You do not have appropriate permissions to start a container"
        return res

    exit_val = 5
    if container_exists(cmd_dict["container_name"]):
        exit_val = command.Command(cmd_dict["cmd_list"]).execute()
        #print command.Command(cmd_list).execute(return_output=True).get("comm_retval")
        if exit_val < 0:
            sys.stderr.write("exit value was", exit_val)
        res = True
    else:
        print cmd_dict["container_name"], "container does not exist"
                       
    return [res, exit_val]


def __stop(cmd_dict):
    res = False

    if not root_access():
        return res

    if not check_input(cmd_dict["container_name"]):
        return res

    exit_val = 5
    if container_exists(cmd_dict["container_name"]):
        exit_val = command.Command(cmd_dict["cmd_list"]).execute()
       # print command.Command(cmd_list).execute(return_output=True).get("comm_retval")
        res = True
    else:
        print cmd_dict["container_name"], "container does not exist"

    return [res, exit_val]


def pi_info():
    # issue #1 is caused somewhere here,
    # documentation for psutil says the following call should be what I'm looking for,
    # but always returns 100 percent...
    # see issue #1 comments
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_total = psutil.virtual_memory().total / 1024
    ram_used = psutil.virtual_memory().used / 1024
    return {"cpu_usage": cpu_usage,
            "ram_total": ram_total,
            "ram_used": ram_used}


def check_input(to_check):
    # checks input for non-printable characters,
    # returns true if to_check has no non-printable characters
    return all(char in string.printable for char in to_check)


def list_containers():
    # returns list of all current container names
    __get_containers()
    global __containers
    return __containers


def container_exists(container_name):
    __get_containers()
    global __containers
    return container_name in __containers


def get_container_usage(container_name):
    if container_exists(container_name):
        # following calculation returns value in MiB
        print (container_usage.memory(container_name)/1024.0)/1024.0
    return


def start_container(container_name):
    # stupid way of doing this (repetition of container name)
    return __start({"cmd_list": ["lxc-start", "-n", container_name, "-d"], "container_name": container_name})


def stop_container(container_name):
    return __stop({"cmd_list": ["lxc-stop", "-n", container_name], "container_name": container_name})