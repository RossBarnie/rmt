# Script to start an LXC container, assumes dependencies resolved
# assuming linux platform

import os
#import sys
import stat
import subprocess

# hard-coding test container for now

# need root access to start containers

def need_root_access():
    root = subprocess.call(["./check_permissions.sh"])
    return root
    

def start():
    if need_root_access() == 0:
        subprocess.call(["lxc-start", "-n", "test", "-d"])
        print subprocess.call(["lxc-info", "-n", "test"])




