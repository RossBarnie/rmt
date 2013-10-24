import subprocess
import threading
import Queue



class Command:
    """ Class to represent an OS-level command """

    def __init__(self, comm):
        self.comm = comm
        self.queue = Queue.Queue(maxsize=10)

    def __execute_com(self, return_output):
        if return_output:
            self.queue.put(subprocess.check_output(self.comm))
            return
        self.queue.put(subprocess.call(self.comm))
        return

    def execute(self, return_output=False, timeout=10.0):
        t = threading.Thread(name="executor", target=self.__execute_com, args=[return_output])
        t.start()
        t.join(timeout=timeout)
        is_timedout = t.isAlive()
        try:
            comm_retval = self.queue.get()
        except Queue.Empty:
            comm_retval = None

        return {"is_timedout": is_timedout, "comm_retval": comm_retval}
