from Config import *
from Marshal import *
import os, sys, socket, optparse, time

# TODO:
# Service 4,5: idempotent op & non-idempotent op
# 4: Delete character in file, 5: Count characters in file

class Client:
    def __init__(self):
        self.invocation = AT_LEAST_ONCE
        self.cache = [0, 0, ''] # cache = [Tvalid, Tclient, cacheEntry]
        self.HOST = 'localhost'
        self.PORT = 7777
        self.freshness_interval = 10
    
    def run(self):
        print('Starting client socket...')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            print("Failed to create client socket:\n{}".format(e))
            sys.exit()
        
        while True:
            print('CACHE: {}'.format(self.cache))
            print('Choose service:\n1: Read content of file. Specify file pathname, offset(in bytes) and no. of bytes.\n')
            print('2: Insert content into file. Specify file pathname, offset(in bytes) and sequence of bytes to write into file.\n')
            print('3: Monitor updates of a file.\n')

            userChoice = input('Input 1-3 or "q" to exit:')

            if userChoice == '1':
                filePathname = input('Input file path name:')
                findFile = self.findFile(filePathname)

                if findFile == True:
                    offset = int(input('Input offset in bytes:'))
                    numBytes = int(input('Input number of bytes:'))
                    check = self.checkCache()
                    if not check:
                        print('Retrieved from Cache: {}'.format(self.cache[-1]))
                    else:
                        print('Server Reply: {}'.format(self.queryRead(filePathname, offset, numBytes)[-1]))
                else:
                    print('File does not exist on server')

            elif userChoice == '2':
                filePathname = input('Input file path name:')
                findFile = self.findFile(filePathname)
                if findFile:
                    offset = int(input('Input offset in bytes:'))
                    seq = input('Input sequence of bytes:')
                    print('Server Reply: {}'.format(self.queryInsert(filePathname, offset, seq)[-1]))
                else:
                    print('File does not exist on server')

            elif userChoice == '3':
                filePathname = input('Input file path name:')
                findFile = self.findFile(filePathname)
                if findFile:
                    monitorInterval = float(input('Input length of monitor interval in seconds:'))
                    print('Server Reply: {}'.format(self.queryMonitor(filePathname, monitorInterval)))

                    timeStart = time.time()
                    while time.time() < monitorInterval + timeStart:
                        try:
                            self.sock.settimeout(monitorInterval)
                            data, address = self.sock.recvfrom(4096)
                            update = unpack(data)[-1]
                            print('Update made to {}: {}'.format(filePathname, update))
                            self.cache[-1] = update

                            # When receive update, reduce interval timeout of socket
                            timeNow = time.time()
                            monitorInterval -= (timeNow - timeStart)
                        except socket.timeout:
                            print('Monitoring of file "{}" ended.'.format(filePathname))
                            self.queryMonitor(filePathname, monitorInterval)
                else:
                    print('File does not exist on server')

            elif userChoice == 'q':
                self.close()
                break
            else:
                print('You have entered an incorrect service. Please input a number from 1-3.\n')

        return

    def send(self, msg):
        while True:
            try:
                self.sock.sendto(pack(msg), (self.HOST, self.PORT))
                data, address = self.sock.recvfrom(4096)
                reply = unpack(data)
                #print('Reply: {}'.format(reply))
                if reply[0] == 0:
                    self.cache[1] = reply[-1]
                return reply
            except socket.timeout:
                print('Timeout')
            except Exception as e:
                print('Error occured while sending: {}'.format(e))

    def close(self):
        print('Closing socket...')
        try:
            self.sock.close()
        except socket.error as e:
            print('Error closing socket:\n{}'.format(e))
        print('Socket closed...')

    def findFile(self, filePathname):
        item = self.send([10, 1, STR, filePathname])
        if item[-1] == 'File exists on server':
            return True
        else:
            return False

    def queryRead(self, filePathname, offset, numBytes):
        item = self.send([1, 3, STR, INT, INT, filePathname, offset, numBytes])
        errors = ["File does not exist on server", "Offset exceeds file length"]
        if item[-1] in errors:
            self.cache[0], self.cache[1] = 0, 0
        else:
            self.cache[2] = item[-1]
        return item

    def queryInsert(self, filePathname, offset, seq):
        item = self.send([2, 3, STR, INT, STR, filePathname, offset, seq])
        self.cache[-1], self.cache[1] = item[-1], item[-2]
        return item

    def queryMonitor(self, filePathname, monitorInterval):
        item = self.send([3, 2, STR, FLT, filePathname, monitorInterval])
        return item

    def checkCache(self):
        Tvalid, Tclient = self.cache[0], self.cache[1]
        if self.cache == '':
            print('Cache entry empty. Send req to server')
            return True
        Tnow = time.time()
        
        if Tnow - Tvalid < self.freshness_interval:
            print('Does not need access to server, read from cache')
            return False
        elif Tnow - Tvalid >= self.freshness_interval:
            Tserver = self.send([0, 1, STR, 'Get Tserver'])[-1] # obtain Tserver
            self.cache[0] = Tnow
            if Tclient == Tserver:
                print('Cache entry valid. Data not modified at server.')
                return False
            elif Tclient < Tserver:
                print('Cache entry invalid. Send req to server')
                return True

if __name__ == "__main__":

    parser = optparse.OptionParser()

    parser.add_option('-t', '--freshness_interval',
        action="store", dest="freshness_interval",
        help='Sets the freshness interval of the client',
        default=10
    )

    parser.add_option('-s', '--semantics_invocation',
        action="store", dest="semantics_invocation",
        help='Sets the semantics invocation used between client & server',
        default=AT_LEAST_ONCE
    )

    parser.add_option('-i', '--ip_server',
        action="store", dest="ip",
        help='Sets the ip address of the server for client to send data to',
        default='localhost'
    )

    parser.add_option('-p', '--port',
        action="store", dest="port",
        help='Sets the port of the server for client to send data to',
        default=7777
    )

    options, args = parser.parse_args()

    client = Client()

    if options.semantics_invocation == AT_LEAST_ONCE:
        client.invocation = AT_LEAST_ONCE
    elif options.semantics_invocation == AT_MOST_ONCE:
        client.invocation = AT_MOST_ONCE

    client.freshness_interval = options.freshness_interval
    client.PORT = int(options.port)
    client.HOST = str(options.ip)
    client.run()