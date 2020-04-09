import socket, logging, time

class Server:

    def __init__(self):
        self.port = 1000
        self.ip = "localhost"
        self.cache = [] # list for last limit requests & responess for at-most-once invocation semantics
        self.monitor = [] # list for monitoring
        self.time = time.process_time()


    