# Script to start an LXC container, assumes dependencies resolved
import command
import string
import psutil
import os

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
    

def root_access():
    return __euid == 0
    

def start(container_name):
    res = False
    __get_containers()

    if not check_input(container_name):
        print "Invalid input\n"
        return res

    if not root_access():
        print "You do not have appropriate permissions to start a container"
        return res

    if container_exists(container_name):
        command.Command(["lxc-start", "-n", container_name, "-d"]).execute().get("comm_retval")
        print command.Command(["lxc-info", "-n", container_name]).execute(return_output=True).get("comm_retval")
        res = True
    else:
        print container_name, "container does not exist"
                       
    return res


def stop(container_name):
    __get_containers()
    res = False

    if not root_access():
        return res

    if not check_input(container_name):
        return res

    if container_exists(container_name):
        command.Command(["lxc-stop", "-n", container_name]).execute().get("comm_retval")
        print command.Command(["lxc-info", "-n", container_name]).execute(return_output=True).get("comm_retval")
        res = True
    else:
        print container_name, "container does not exist"

    return res


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
    __get_containers()
    global __containers
    for c in __containers:
        print c
    return


def container_exists(container_name):
    global __containers
    return container_name in __containers
