import httpx
import threading

# TODO: i want to deprecate this
class Requestor:
    """A context manager used to ensure that a delay is made between requests.
    Works when requests are looped and one request depends on the previous. The
    requestor essentially blocks on the second request until the timer has
    finished. In between requests however it does not block, so allows processing.
    
    e.g. My requestor has a delay of 10s. I make a request in 1s and process it in 2s (total 3s). I make
    another request. It waits for 7s before it makes the request.
    """
    def __init__(self, client: httpx.AsyncClient, delay: int = 0):
        self.delay = delay
        self.client = client
        self.blocked = False
        self.timer = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if self.timer:
            self.timer.cancel()

    def get(self, *args, **kwargs):
        while True:
            if not self.blocked:
                self.timer = threading.Timer(self.delay, self.unblock)
                self.timer.start()
                r = self.client.get(*args, **kwargs)
                self.blocked = True
                return r

    def unblock(self):
        self.blocked = False
