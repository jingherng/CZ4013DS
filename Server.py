import socket, logging, time

class Server:
    def __init__(self):
        self.UDP_ip = "127.0.0.1"
        self.UDP_port = 5005
        self.cache = [] # list for last limit requests & responess for at-most-once invocation semantics
        self.monitor = [] # list for monitoring
        self.time = time.process_time()

    def run(self):
        self.sock = socket.socket(socket.AF_INET, # Internet
                                    socket.SOCK_DGRAM) # UDP

        # bind socket to port
        serverAddress = (self.UDP_ip, self.UDP_port)
        logging.info('Starting server on {} Port {}'.format(self.UDP_ip, self.UDP_port))
        self.sock.bind(serverAddress)
        
        self.await()

    def await(self):
        while True:
            logging.info('Awaiting data from client...')
            data, address = self.sock.recvfrom(4096)
            logging.info('Received data from {}: {}'.format(data, address))
            self.replyReq(data, address)

    def replyReq(self, data, address):
        return

logging.basicConfig(filename='logs.log',level=logging.DEBUG)