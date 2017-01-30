import threading
import time


class _thread(threading.Thread):
    
    def __init__(self):
        
        threading.Thread.__init__(self) # init the thread
        self.stopevent = threading.Event()
        # to avoid the thread to be started more than once
        self._started = False 
        # recording last time the actions were done
        self._last_thread_action = 0

         
    def start(self):
        # this methods is overriden
        # to prevent the thread from being started more than once.
        # That could happen if the final threading class
        # implements the design pattern Singleton.
        # In that cases, multiple copies of the same object
        # may be instantiated, and eventually "started"
        
        if not self._started:
            self._started = True
            threading.Thread.start(self)


    def join(self,timeout=None):
        if not self.stopevent.isSet():
            self.stopevent.set()
            threading.Thread.join(self, timeout)


    def run(self):                
        while not self.stopevent.isSet():
            try:                       
                if self._check_for_actions():
                    self._run()
                    self._last_thread_action = int( time.time() )
            except Exception, e:
                if self._propagate_exception():
                    raise e
                if self._abort_on_exception():
                    self.join()
                self._last_thread_action = int( time.time() )
            self._wait_for_abort()


    def _check_for_actions(self):
        '''
        checks if a new loop of action should take place
        '''
        # default implementation
        return int(time.time()) - self._last_thread_action > self._time_between_loops()


    def _time_between_loops(self):
        '''
        returns the amount of time to wait between action cycles
        '''
        raise NotImplementedError


    def _wait_for_abort(self):
        '''
        waits for the loop to be aborted because the thread has been killed
        '''
        time.sleep( self._wait() )


    def _wait(self):
        '''
        returns the amount of time to wait before checking again for interrupt. Defaults to 1 second.
        '''
        # reimplement this method if response is not 1 second 
        return 1
        

    def _propagate_exception(self):
        '''
        boolean to decide if the Exception needs to be propagated. Defaults to False.
        '''
        # reimplement this method if response is not unconditionally False
        return False 


    def _abort_on_exception(self):
        '''
        boolean to decide if the Exception triggers the thread to be killed. Defaults to False.
        '''
        # reimplement this method if response is not unconditionally False
        return False 


    def _run(self):
        raise NotImplementedError


