import socket, time, sys

class Server:
    def __init__(self):
        self.UDP_ip = "127.0.0.1"
        self.UDP_port = 7777
        self.cache = [] # list for last limit requests & responess for at-most-once invocation semantics
        self.monitor = [] # list for monitoring
        self.time = time.process_time()

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, # Internet
                                        socket.SOCK_DGRAM) # UDP
        except socket.error as e:
            print('Failed to create socket:\n{}'.format(e))
            sys.exit()

        # bind socket to port
        serverAddress = (self.UDP_ip, self.UDP_port)
        print('Starting server on {} Port {}...'.format(self.UDP_ip, self.UDP_port))

        try:
            self.sock.bind(serverAddress)
        except socket.error as e:
            print('Socket bind failed:\n{}'.format(e))
            sys.exit()
        

        # once socket bind, keep talking to client
        self.await()


    # await data from client
    def await(self):
        while True:
            print('Awaiting data from client...')
            data, address = self.sock.recvfrom(4096)
            data = data.decode('utf-8')
            print('Received data from {}:\n{}'.format(address, data))
            if data == 'q':
                self.sock.sendto( bytes('q', 'utf-8'), address)
                self.close()
                return
            self.replyReq(data, address)

    def replyReq(self, data, address):

        ## processing of data
        reply = self.processReq(data)
        ## reply variable encoded in bytes utf-8
        reply = bytes(reply, 'utf-8')
        self.sock.sendto(reply, address)
        return

    def close(self):
        print('Closing socket...')
        try:
            self.sock.close()
        except socket.error as e:
            print('Error closing socket:\n{}'.format(e))
        print('Socket closed...')

    def processReq(self, data):
        if not data:
            return 'Request not found.'

        d = data.split()
        
        if len(d) == 4:
            service = d[0]
            filePathName = d[1]
            offset = d[2]
            numBytes = d[3]
        else:
            service = d[0]
            filePathName = d[1]
            monitorInterval = d[2]

        if service == '1': # Read content of file
            return self.readFile(filePathName, offset, numBytes)
        
        elif service == '2': # Insert content into file
            return self.insertContent(filePathName, offset, numBytes)
        
        elif service == '3': # Monitor updates made to content of specified file
            return self.monitorFile(filePathName, monitorInterval)

    
    def readFile(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            f.seek(int(offset), 0)
            content = f.read(int(numBytes))
            f.close()
            return content
        except FileNotFoundError as e:
            return str(e)

    def insertContent(self, filePathName, offset, numBytes):
        return

    def monitorFile(self, filePathName, monitorInterval):
        return


if __name__ == "__main__":
    server = Server()
    server.run()