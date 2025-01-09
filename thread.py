import threading


class thread:
    def __init__(self, func: callable):
        self.main = func

    def main(self): pass

    def join(self): return self.thread.join()

    def __call__(self, *args, **kwargs):
        self.thread = threading.Thread(target=self.main, args=args, kwargs=kwargs)
        self.thread.start()
        return self.thread
