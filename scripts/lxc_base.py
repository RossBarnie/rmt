# Script to start an LXC container, assumes dependencies resolved


import subprocess
import string

# hard-coding test container for now

# need root access to start containers


CONTAINERS = []

def get_containers():
    global CONTAINERS 
    CONTAINERS = subprocess.check_output(["lxc-ls"])
    CONTAINERS = CONTAINERS.splitlines()
    

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
    # needs work...need to parse alot of this, may look for alternatives
    info = subprocess.check_output(["top", "-n", "1"]).splitlines()
    print info[0]


def check_input(to_check):
    # checks input for non-printable characters,
    # returns true if to_check has no non-printable characters
    return all(char in string.printable for char in to_check)


def container_exists(container_name):
    global CONTAINERS
    return container_name in CONTAINERS
