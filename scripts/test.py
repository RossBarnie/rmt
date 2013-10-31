__author__ = 'ross'

import lxc_base
import time

lxc_base.start("test")

time.sleep(5)

lxc_base.stop("test")

keys = lxc_base.pi_info().keys()
for key in keys:
    print key, lxc_base.pi_info().get(key)