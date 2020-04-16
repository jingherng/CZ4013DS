from Marshal import *
from Config import *
import socket
import time
import sys
import random
import optparse


class Server:
    def __init__(self):
        self.UDP_ip = "127.0.0.1"
        self.UDP_port = 7777
        self.time = time.time()
        self.cache = []
        self.cacheLimit = 10
        self.monitorList = []  # monitoring list format: [address, filePathname]
        self.invocationSemantics = 'AT_LEAST_ONCE'
        self.simulateLoss = True

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
        except socket.error as e:
            print('Failed to create socket:\n{}'.format(e))
            sys.exit()

        # bind socket to port
        serverAddress = (self.UDP_ip, self.UDP_port)
        print('Starting server on {} Port {}...'.format(
            self.UDP_ip, self.UDP_port))

        print('Invocation semantics used: {}'.format(self.invocationSemantics))
        
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
            #print('Monitor List: {}'.format(self.monitorList))
            print('Awaiting data from client...')
            data, address = self.sock.recvfrom(4096)
            print('Received data from {}:\n{!r}'.format(address, data))
            # if address not in self.clientList:
            #    self.clientList.append(address)
            self.replyReq(data, address)

    def replyReq(self, data, address):
        if self.invocationSemantics == 'AT_LEAST_ONCE':
            self.replyAtLeastOnce(data, address)
        elif self.invocationSemantics == 'AT_MOST_ONCE':
            self.replyAtMostOnce(data, address)
        return

    def close(self):
        print('Closing socket...')
        try:
            self.sock.close()
        except socket.error as e:
            print('Error closing socket:\n{}'.format(e))
        print('Socket closed...')

    def processReq(self, data, address):
        if not data:
            return 'Request not found.'

        d = unpack(data)  # unpacked data as variable, d
        #print("D IS HERE: {}".format(d))

        service = d[0]

        if service == 1:  # Read content of file
            return self.readFile(d[2], d[3], d[4])

        elif service == 2:  # Insert content into file
            self.time = time.time()
            content = self.insertContent(d[2], d[3], d[4])
            self.callback(content, d)
            return content

        elif service == 3:  # Monitor updates made to content of specified file
            return self.monitorFile(d[2], d[3], address)

        elif service == 0:
            return self.sendTserver()

    def sendTserver(self):
        return [0, 1, FLT, self.time]

    def readFile(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            content = f.read()
            f.close()

            if offset > len(content):
                return [1, 1, ERR, "Offset exceeds file length"]

            f = open(filePathName, 'r')
            f.seek(offset, 0)
            content = f.read(int(numBytes))
            f.close()
            return [1, 1, STR, content]
        except FileNotFoundError:
            return [1, 1, ERR, "File does not exist on server"]
        except OSError as e:
            return [1, 1, ERR, str(e)]

    def insertContent(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            content = f.read()
            f.close()

            if offset > len(content):
                return [2, 1, ERR, "Offset exceeds file length"]

            f = open(filePathName, 'w')
            content = content[0:offset] + numBytes + content[offset:]
            f.write(content)
            f.close()

            return [2, 2, FLT, STR, self.time, content]

        except FileNotFoundError:
            return [2, 1, ERR, "File does not exist on server"]
        except OSError as e:
            return [2, 1, ERR, str(e)]

    def monitorFile(self, filePathName, monitorInterval, address):

        try:
            f = open(filePathName, 'r')
            f.close()
        except FileNotFoundError:
            return [3, 1, ERR, "File does not exist on server"]

        if (address, filePathName) not in self.monitorList:
            self.monitorList.append((address, filePathName))
            return [3, 1, STR, '{} added to the monitoring list for {} seconds for file: {}'.format(address, monitorInterval, filePathName)]
        else:
            self.monitorList.remove((address, filePathName))
            return [3, 1, STR, '{} removed from monitoring list since monitor interval ended'.format(address)]

    def callback(self, content, d):
        if len(self.monitorList) > 0:  # Checks if there are clients registered for monitoring
            for i in self.monitorList:  # Loops through whole monitoring list
                if d[2] == i[1]:  # Checks if file is same as file registered for monitoring
                    print('Callback to {}: {}'.format(i[0], content))
                    self.sock.sendto(pack(content), i[0])
        return

    def replyAtLeastOnce(self, data, address):
        reply = self.processReq(data, address)

        if self.simulateLoss and random.randrange(0, 2) == 0:
            self.sock.sendto(pack(reply), address)
        elif self.simulateLoss == False:
            self.sock.sendto(pack(reply), address)

    def replyAtMostOnce(self, data, address):
        # check server cache for existence of request
        # if found, reply client with cacheEntry
        for cacheEntry in self.cache:
            if cacheEntry[0] == [address[0], address[1], data]:
                if self.simulateLoss and random.randrange(0, 2) == 0:
                    self.sock.sendto(pack(cacheEntry[1]), address)
                elif self.simulateLoss == False:
                    self.sock.sendto(pack(cacheEntry[1]), address)
                return

        reply = self.processReq(data, address)

        if len(self.cache) == self.cacheLimit:
            self.cache = self.cache[1:]
        self.cache.append(([address[0], address[1], data], reply))

        if self.simulateLoss and random.randrange(0, 2) == 0:
            self.sock.sendto(pack(reply), address)
        elif self.simulateLoss == False:
            self.sock.sendto(pack(reply), address)


if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option('-i', '--UDP_ip',
                      action="store", dest='UDP_ip',
                      help="Sets the ip address of the server", default="localhost")

    parser.add_option('-p', '--UDP_port',
                      action="store", dest="UDP_port",
                      help="Sets the port of server",
                      default=7777)

    parser.add_option('-s', '--invocationSemantics',
                      action="store", dest="invocationSemantics",
                      help="Sets the invocation semantics",
                      default='AT_LEAST_ONCE')

    server = Server()
    options, args = parser.parse_args()
    server.UDP_ip = str(options.UDP_ip)
    server.UDP_port = int(options.UDP_port)
    server.invocationSemantics = options.invocationSemantics
    server.run()
