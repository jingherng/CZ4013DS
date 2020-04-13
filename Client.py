from Config import *
from Marshal import *
import os, sys, socket

class Client:
    def __init__(self):
        self.UDP_server_IP = "127.0.0.1"
        self.UDP_server_Port = 5005
        self.invocation = [AT_LEAST_ONCE, AT_MOST_ONCE]
        
        self.HOST = 'localhost'
        self.PORT = 7777
    
    def run(self):
        print('Starting client socket...')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            print("Failed to create client socket:\n{}".format(e))
            sys.exit()
        
        while True:
            print('Choose service:\n1: Read content of file. Specify file pathname, offset(in bytes) and no. of bytes.\n')
            print('2: Insert content into file. Specify file pathname, offset(in bytes) and sequence of bytes to write into file.\n')
            print('3: Monitor updates of a file.\n')

            userChoice = input('Input 1-3 or "q" to exit:')

            if userChoice == '1':
                filePathname = input('Input file path name:')
                offset = int(input('Input offset in bytes:'))
                numBytes = int(input('Input number of bytes:'))
                print('Server Reply: {}'.format(self.queryRead(filePathname, offset, numBytes)))
            elif userChoice == '2':
                filePathname = input('Input file path name:')
                offset = int(input('Input offset in bytes:'))
                seq = input('Input sequence of bytes:')
                print('Server Reply: {}'.format(self.queryInsert(filePathname, offset, seq)))
            elif userChoice == '3':
                filePathname = input('Input file path name:')
                monitorInterval = int(input('Input length of monitor interval:'))
                print('Server Reply: {}'.format(self.queryMonitor(filePathname, monitorInterval)))
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

                return data
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
        return unpack(item)

    def queryInsert(self, filePathname, offset, seq):
        item = self.send([2, 3, STR, INT, STR, filePathname, offset, seq])
        return unpack(item)

    def queryMonitor(self, filePathname, monitorInterval):
        item = self.send([3, 2, STR, INT, filePathname, monitorInterval])
        return unpack(item)

if __name__ == "__main__":
    client = Client()
    client.run()