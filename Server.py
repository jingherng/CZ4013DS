import socket, logging, time, sys

class Server:
    def __init__(self):
        self.UDP_ip = "127.0.0.1"
        self.UDP_port = 7777
        self.cache = [] # list for last limit requests & responess for at-most-once invocation semantics
        self.monitor = [] # list for monitoring
        self.time = time.process_time()
        logging.basicConfig(filename='server.log',level=logging.DEBUG)

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, # Internet
                                        socket.SOCK_DGRAM) # UDP
        except socket.error as e:
            logging.error('Failed to create socket {}'.format(e))
            sys.exit()

        # bind socket to port
        serverAddress = (self.UDP_ip, self.UDP_port)
        logging.info('Starting server on {} Port {}'.format(self.UDP_ip, self.UDP_port))

        try:
            self.sock.bind(serverAddress)
        except socket.error as e:
            logging.error('Socket bind failed {}'.format(e))
            sys.exit()
        

        # once socket bind, keep talking to client
        self.await()


    # await data from client
    def await(self):
        while True:
            logging.info('Awaiting data from client...')
            data, address = self.sock.recvfrom(4096)
            logging.info('Received data from {}: {}'.format(data, address))

            if not data:
                logging.info('Data not found')
                break

            self.replyReq(data, address)

    def replyReq(self, data, address):

        ## processing of data
        reply = 'SOME FN()'
        ## reply variable encoded in bytes utf-8
        reply = bytes(reply, 'utf-8')
        self.sock.sendto(reply, address)
        return

    def close(self):
        logging.info('Closing socket...')
        try:
            self.sock.close()
        except socket.error as e:
            logging.error('Error closing socket: {}'.format(e))
        logging.info('Socket closed...')

if __name__ == "__main__":
    server = Server()
    server.run()