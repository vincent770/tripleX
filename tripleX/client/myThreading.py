import threading


# stoppable thread class
class MyThread(threading.Thread):
    def __init__(self, func, *args):
        
        super(MyThread, self).__init__()
        self._stop_event = threading.Event()
        self._stop_event.clear() # 将标志默认设置为False
        
        self.func = func
        self.args = args
        
        self.setDaemon(True)
        self.start()    # 在这里开始
        
    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def current_thread():
        return threading.current_thread()

    def run(self):
        self.func(*self.args)
