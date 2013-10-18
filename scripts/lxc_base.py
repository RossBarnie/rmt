# Script to start an LXC container, assumes dependencies resolved
import subprocess
import string
import psutil

# hard-coding test container for now

# need root access to start containers

_containers = []


def get_containers():
    global _containers
    _containers = subprocess.check_output(["lxc-ls"])
    _containers = _containers.splitlines()
    

def root_access():
    root = subprocess.call(["./check_permissions.sh"])
    return root
    

def start(container_name):
    res = False
    get_containers()

    if not check_input(container_name):
        print "Invalid input\n"
        return res

    if root_access() == 1:
        return res

    if container_exists(container_name):
        subprocess.call(["lxc-start", "-n", container_name, "-d"])
        subprocess.call(["lxc-info", "-n", container_name])
        res = True
    else:
        print container_name, "container does not exist"
                       
    return res


def stop(container_name):
    get_containers()
    res = False

    if root_access() == 1:
        return res

    if not check_input(container_name):
        return res

    if container_exists(container_name):
        subprocess.call(["lxc-stop", "-n", container_name])
        subprocess.call(["lxc-info", "-n", container_name])
        res = True
    else:
        print container_name, "container does not exist"

    return res


def pi_info():
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


def container_exists(container_name):
    global _containers
    return container_name in _containers
