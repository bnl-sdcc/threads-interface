import logging
import threading
import time


class NullHandler(logging.Handler):
    """
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found for logger XXX" one-off warning. This is
    important for library code, which may contain code to log events. If a user
    of the library does not configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler and add it to the top-level logger of the library module or
    package.
    """

    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None



class _thread(threading.Thread):
    
    def __init__(self):

        self.log = logging.getLogger('_thread')
        self.log.addHandler(NullHandler())
        
        threading.Thread.__init__(self) # init the thread
        self.stopevent = threading.Event()
        # to avoid the thread to be started more than once
        self._thread_started = False 
        # recording last time the actions were done
        self._thread_last_action = 0
        # time to wait before checking again if the threads has been killed
        self._thread_abort_interval = 1
        # time to wait before next loop
        self._thread_loop_interval = 1
        self.log.debug('object _thread initialized')

         
    def start(self):
        # this methods is overriden
        # to prevent the thread from being started more than once.
        # That could happen if the final threading class
        # implements the design pattern Singleton.
        # In that cases, multiple copies of the same object
        # may be instantiated, and eventually "started"
        
        if not self._thread_started:
            self.log.debug('starting thread')
            self._thread_started = True
            threading.Thread.start(self)


    def join(self,timeout=None):
        if not self.stopevent.isSet():
            self.log.debug('joining thread')
            self.stopevent.set()
            threading.Thread.join(self, timeout)


    def run(self):
        self.log.debug('starting run()')
        self._prerun()
        self._mainloop()
        self._postrun()
        self.log.debug('leaving run()')
    

    def _prerun(self):
        '''
        actions to be done before starting the main loop
        '''
        # default implementation is to do nothing
        pass

    
    def _postrun(self):
        '''
        actions to be done after the main loop is finished
        '''
        # default implementation is to do nothing
        pass

    
    def _mainloop(self):
        while not self.stopevent.isSet():
            try:                       
                if self._check_for_actions():
                    self._run()
                    self._thread_last_action = int( time.time() )
            except Exception, e:
                if self._propagate_exception():
                    raise e
                if self._abort_on_exception():
                    self.join()
                self._thread_last_action = int( time.time() )
            self._wait_for_abort()


    def _check_for_actions(self):
        '''
        checks if a new loop of action should take place
        '''
        # default implementation
        now = int(time.time())
        check = (now - self._thread_last_action) > self._thread_loop_interval
        return check


    def _wait_for_abort(self):
        '''
        waits for the loop to be aborted because the thread has been killed
        '''
        time.sleep( self._thread_abort_interval )


    def _propagate_exception(self):
        '''
        boolean to decide if the Exception needs to be propagated. 
        Defaults to False.
        '''
        # reimplement this method if response is not unconditionally False
        return False 


    def _abort_on_exception(self):
        '''
        boolean to decide if the Exception triggers the thread to be killed. 
        Defaults to False.
        '''
        # reimplement this method if response is not unconditionally False
        return False 


    def _run(self):
        raise NotImplementedError


# =============================================================================
# Example of usage

if __name__ == "__main__":
    

    class MyClass(_thread):
        def __init__(self):
            _thread.__init__(self)
            self._thread_loop_interval = 2

        def _run(self):
            """
            main loop
            """
            print "thread running"

    t = MyClass()
    t.start()
    time.sleep(10)
    t.join()



