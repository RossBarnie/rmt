__author__ = 'ross'

import lxc_base
import time

print lxc_base.start({"cmd_list": ["lxc-start", "-n", "test", "-d"], "container_name": "test"})

time.sleep(5)

print lxc_base.stop({"cmd_list": ["lxc-stop", "-n", "test"], "container_name": "test"})

keys = lxc_base.pi_info().keys()
for key in keys:
    print key, lxc_base.pi_info().get(key)