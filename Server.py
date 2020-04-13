from Marshal import *
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
            print('Received data from {}:\n{!r}'.format(address, data))
            if data == 'q':
                self.sock.sendto( bytes('q', 'utf-8'), address)
                self.close()
                return
            self.replyReq(data, address)

    def replyReq(self, data, address):

        ## processing of data
        reply = self.processReq(data)
        print('Reply: {}'.format(reply))
        self.sock.sendto(pack(reply), address)
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

        d = unpack(data)
        #print("D IS HERE: {}".format(d))

        service = d[0]

        if service == 1: # Read content of file
            return self.readFile(d[2], d[3], d[4])
        
        elif service == 2: # Insert content into file
            return self.insertContent(d[2], d[3], d[4])
        
        elif service == 3: # Monitor updates made to content of specified file
            return self.monitorFile(d[2], d[3])

    
    def readFile(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            f.seek(offset, 0)
            content = f.read(int(numBytes))
            f.close()
            if content:
                return [1, 1, STR, content]
            else:
                return [1, 1, STR, "Offset exceeds file length"]
        except FileNotFoundError:
            return [1, 1, STR, "File does not exist on server"]
        except OSError as e:
            return [1, 1, STR, str(e)]

    def insertContent(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            content = f.read()
            f.close()

            if offset > len(content):
                return [1, 1, STR, "Offset exceeds file length"]

            f = open(filePathName, 'w')
            content = content[0:offset] + numBytes + content[offset:]
            f.write(content)
            f.close()

            return [1, 1, STR, content]

        except FileNotFoundError:
            return [1, 1, STR, "File does not exist on server"]
        except OSError as e:
            return [1, 1, STR, str(e)]

    def monitorFile(self, filePathName, monitorInterval):
        return


if __name__ == "__main__":
    server = Server()
    server.run()