from Config import *
from Marshal import *
import os
import sys
import socket
import optparse
import time
import random


class Client:
    def __init__(self):
        self.cache = [0, 0, '']  # cache = [Tvalid, Tclient, cacheEntry]
        self.HOST = 'localhost'
        self.PORT = 7777
        self.freshness_interval = 10
        self.simulateLoss = False

    def run(self):
        print('Starting client socket...')

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(1)
        except socket.error as e:
            print("Failed to create client socket:\n{}".format(e))
            sys.exit()

        while True:
            print('Choose a service according to the following options:\n')
            print('1: Read content of file. Specify file pathname, offset(in bytes) and no. of bytes.\n')
            print('2: Insert content into file. Specify file pathname, offset(in bytes) and sequence of bytes to write into file.\n')
            print('3: Monitor updates of a file.\n')
            print('4: Calculate length of content in file.\n')
            print('5: Create a new file.\n')

            userChoice = input('Input 1-5 or "q" to exit:')

            if userChoice == '1':
                filePathname = input('Input file path name:')
                offset = int(input('Input offset in bytes:'))
                numBytes = int(input('Input number of bytes:'))
                check = self.checkCache()
                if not check:
                    print('Retrieved from Cache: {}'.format(self.cache[-1]))
                else:
                    print('Server Reply: {}'.format(
                        self.queryRead(filePathname, offset, numBytes)[-1]))

            elif userChoice == '2':
                filePathname = input('Input file path name:')
                offset = int(input('Input offset in bytes:'))
                seq = input('Input sequence of bytes:')
                print('Server Reply: {}'.format(
                    self.queryInsert(filePathname, offset, seq)[-1]))

            elif userChoice == '3':
                filePathname = input('Input file path name:')
                monitorInterval = float(input('Input length of monitor interval in seconds:'))

                if monitorInterval < 0.0:
                    print('Monitor interval input invalid.')
                else:
                    reply = self.queryMonitor(filePathname, monitorInterval)[-1]
                    print('Server Reply: {}'.format(reply))
                    if reply != 'File does not exist on server':
                        timeStart = time.time()
                        while monitorInterval > 0:
                            try:
                                self.sock.settimeout(monitorInterval)
                                data, address = self.sock.recvfrom(4096)
                                update = unpack(data)[-1]
                                print('Update made to {}: {}'.format(
                                    filePathname, update))
                                self.cache[-1] = update

                                # When receive update, reduce interval timeout of socket
                                timeNow = time.time()
                                monitorInterval -= (timeNow - timeStart)
                            except socket.timeout:
                                self.queryMonitor(filePathname, monitorInterval)
                                break
                        print('Monitoring of file "{}" ended.'.format(filePathname))
                        self.queryMonitor(filePathname, monitorInterval)

            elif userChoice == '4':
                filePathname = input('Input file path name:')
                print('Server Reply: {} characters in {}'.format(
                    self.queryCount(filePathname)[-1], filePathname))

            elif userChoice == '5':
                fileName = input('Input file name:')
                char = str(input('Input file content:'))
                reply = self.queryCreate(fileName, char)[-1]
                print('Server Reply: {}'.format(reply))

            elif userChoice == 'q':
                self.close()
                break
            else:
                print('You have entered an incorrect service.')
                print('Please input a number from 1-5 or "q" to exit.\n')

        return

    def send(self, msg):
        while True:
            try:
                # Simulate packet loss based on invocation scheme
                if self.simulateLoss and random.randrange(0, 2) == 0:
                    self.sock.sendto(pack(msg), (self.HOST, self.PORT))
                elif self.simulateLoss == False:
                    self.sock.sendto(pack(msg), (self.HOST, self.PORT))

                data, address = self.sock.recvfrom(4096)
                reply = unpack(data)
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

    def queryRead(self, filePathname, offset, numBytes):
        item = self.send([1, 3, STR, INT, INT, filePathname, offset, numBytes])
        errors = ["File does not exist on server",
                  "Offset exceeds file length"]
        if item[-1] in errors:
            self.cache[0], self.cache[1] = 0, 0
        else:
            self.cache[2] = item[-1]
        return item

    def queryInsert(self, filePathname, offset, seq):
        item = self.send([2, 3, STR, INT, STR, filePathname, offset, seq])
        errors = ["File does not exist on server",
                  "Offset exceeds file length"]
        if item[-1] not in errors:
            self.cache[-1], self.cache[1] = item[-1], item[-2]
        return item

    def queryMonitor(self, filePathname, monitorInterval):
        item = self.send([3, 2, STR, FLT, filePathname, monitorInterval])
        return item

    def queryCount(self, filePathname):
        item = self.send([4, 1, STR, filePathname])
        return item

    def queryCreate(self, fileName, char):
        item = self.send([5, 2, STR, STR, fileName, char])
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
            Tserver = self.send([0, 1, STR, 'Get Tserver'])[-1]  # fn to obtain Tserver
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

    client.freshness_interval = options.freshness_interval
    client.PORT = int(options.port)
    client.HOST = str(options.ip)

    client.run()
