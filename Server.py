from Marshal import *
import socket, time, sys

class Server:
    def __init__(self):
        self.UDP_ip = "127.0.0.1"
        self.UDP_port = 7777
        self.time = time.time()
        self.clientList = []
        self.monitorList = []

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
            print('Monitor List: {}'.format(self.monitorList))
            print('Awaiting data from client...')
            data, address = self.sock.recvfrom(4096)
            print('Received data from {}:\n{!r}'.format(address, data))
            if address not in self.clientList:
                self.clientList.append(address)
            self.replyReq(data, address)

    def replyReq(self, data, address):

        ## processing of data
        reply = self.processReq(data, address)
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

    def processReq(self, data, address):
        if not data:
            return 'Request not found.'

        d = unpack(data)
        #print("D IS HERE: {}".format(d))

        service = d[0]
        if service == 10:
            return self.findFile(d[2])

        if service == 1: # Read content of file
            return self.readFile(d[2], d[3], d[4])
        
        elif service == 2: # Insert content into file
            self.time = time.time()
            content = self.insertContent(d[2], d[3], d[4])
            if len(self.monitorList) > 0:
                for i in self.monitorList:
                    if d[2] == i[1]:
                        print('Update sent to {}: {}'.format(i[0], content))
                        self.sock.sendto(pack(content), i[0])
            return content
        
        elif service == 3: # Monitor updates made to content of specified file
            return self.monitorFile(d[2], d[3], address)

        elif service == 0:
            return self.sendTserver()

    def sendTserver(self):
        return [0, 1, FLT, self.time]

    def findFile(self, filePathName):
        try:
            f = open(filePathName, 'r')
            f.close()
            return [10, 1, STR, 'File exists on server']
        except FileNotFoundError:
            return [10, 1, ERR, "File does not exist on server"]
        except Exception as e:
            return [10, 1, ERR, str(e)]

    
    def readFile(self, filePathName, offset, numBytes):
        try:
            f = open(filePathName, 'r')
            f.seek(offset, 0)
            content = f.read(int(numBytes))
            f.close()
            if content:
                return [1, 1, STR, content]
            else:
                return [1, 1, ERR, "Offset exceeds file length"]
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
        if (address, filePathName) not in self.monitorList:
            self.monitorList.append((address, filePathName))
        else:
            self.monitorList.remove((address, filePathName))
        return [3, 1, STR, '{} added to the monitoring list for {} seconds for file: {}'.format(address, monitorInterval, filePathName)]


if __name__ == "__main__":
    server = Server()
    server.run()