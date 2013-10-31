import subprocess
import threading
import Queue


class Command:
    """ Class to represent an OS-level command """

    def __init__(self, comm):
        self.comm = comm
        self.queue = Queue.Queue(maxsize=10)

    def __execute_com(self, return_output):
        try:
            proc = subprocess.Popen(self.comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode < 0:
                print "command ", self.comm, "was terminated by signal", proc.returncode
            if return_output:
                self.queue.put(out, timeout=5)
        except subprocess.CalledProcessError as e:
            print "command", self.comm, "caused exception, ", e
        return

    def execute(self, return_output=False, timeout=10.0):
        t = threading.Thread(name="executor", target=self.__execute_com, args=[return_output])
        t.start()
        t.join(timeout=timeout)
        is_timedout = t.isAlive()
        comm_retval=""
        try:
            if return_output:
                comm_retval = self.queue.get()
        except Queue.Empty:
            comm_retval = None

        return {"is_timedout": is_timedout, "comm_retval": comm_retval}
