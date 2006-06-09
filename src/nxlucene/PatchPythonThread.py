# PyLucene memory leak fix !
# See http://lists.osafoundation.org/pipermail/pylucene-dev/2006-May/001022.html

# $Id: $

from PyLucene import Thread
import threading

# A few kludges here because starting the OS thread is done by libgcj
# instead of python.
    
class PythonThread(threading.Thread):
    """
    A threading.Thread extension that delegates starting of the
    actual OS thread to libgcj. In order to keep libgcj's garbage collector
    happy, any python thread using libgcj must be of this class.
    """

    def __init__(self, *args, **kwds):

        super(PythonThread, self).__init__(*args, **kwds)
        self.javaThread = None

    def start(self):

        current = threading.currentThread()
        assert (current.getName() == 'MainThread' or isinstance(current, PythonThread)), "PythonThread can only be started from main thread of from another PythonThread"
        
        class runnable(object):
            def __init__(_self, callable):
                _self.callable = callable
            def run(_self):
                try:
                    _self.callable()
                finally:
                    del _self.callable
                    self.javaThread = None

        threading._active_limbo_lock.acquire()
        threading._limbo[self] = self
        threading._active_limbo_lock.release()
        
        thread = self.javaThread = Thread(runnable(self._Thread__bootstrap),
                                          self.getName())
        thread.start()

        self._Thread__started = True

    def join(self, timeout=None):

        thread = self.javaThread
        if thread is not None:
            if timeout is not None:
                thread.join(long(timeout * 1000))
            else:
                thread.join()
