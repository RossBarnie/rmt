import threading


def dummy_func():
    print t1.getName(), "executing"
    return

t1 = threading.Thread(name="executor", target=dummy_func)
t1.start()
t1.join(timeout=0.001)
if t1.isAlive():
    print "timed out"
else:
    print "success"



