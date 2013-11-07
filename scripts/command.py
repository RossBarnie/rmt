import subprocess
import threading
import Queue
import sys


class Command:
    """ Class to represent an OS-level command """

    def __init__(self, comm):
        self.comm = comm
        self.queue = Queue.Queue(maxsize=10)
        self.process = None

    def execute(self, return_output=False, timeout=10.0):

        def target():
            try:
                print "Starting command"
                self.process = subprocess.Popen(self.comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = self.process.communicate()
                if self.process.returncode < 0:
                    print "command ", self.comm, "was terminated by signal", self.process.returncode
                if return_output:
                    self.queue.put(out, timeout=1)
            except subprocess.CalledProcessError as e:
                print "command", self.comm, "caused exception, ", e
            return

        thread = threading.Thread(target=target)
        print "starting thread"
        thread.start()
        print "joining with timeout of", timeout
        thread.join(timeout=timeout)
        print "finished initial join"
        is_alive = thread.is_alive()
        if is_alive:
            print "thread is alive, terminating process"
            self.process.terminate()
            print "joining thread, no timeout specified"
            thread.join()
        comm_retval = None
        if return_output:
            try:
                comm_retval = self.queue.get(timeout=1)
            except Queue.Empty:
                sys.stderr.write("Queue access attempted but was empty, returning None")

        return {"is_timedout": is_alive, "returncode": self.process.returncode, "comm_retval": comm_retval}
