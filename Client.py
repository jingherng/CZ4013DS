from Config import *
import os, sys, socket

class Client:
    def __init__(self):
        self.UDP_server_IP = "127.0.0.1"
        self.UDP_server_Port = 5005
        self.invocation = [AT_LEAST_ONCE, AT_MOST_ONCE]
    
    def run(self):
        print('Starting client socket...')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            print("Failed to create client socket:\n{}".format(e))
            sys.exit()

        HOST = 'localhost'
        PORT = 7777
        
        print('Choose service:\n1: Read content of file. Specify file pathname, offset(in bytes) and no. of bytes.\n')
        print('2: Insert content into file. Specify file pathname, offset(in bytes) and sequence of bytes to write into file.\n')
        print('3: Monitor updates of a file.\n')

        data = input('Enter an option and the corressponding data(Enter "q" to quit): ')

        while True:
            msg = bytes(data, 'utf-8')
            try:
                self.sock.sendto(msg, (HOST, PORT))
            except socket.error as e:
                print('Error sending request: {}'.format(e))

            
            try:
                data, address = self.sock.recvfrom(4096)
                data = data.decode('utf-8')
                if data == 'q':
                    self.close()
                    break
                #print('Server reply:\n{}'.format(data))
                print('{}'.format(data))

            except socket.error as e:
                print('Error receiving message:\n{}'.format(e))

            data = input('Enter a request (Press q to quit): ')

        return

    def close(self):
        print('Closing socket...')
        try:
            self.sock.close()
        except socket.error as e:
            print('Error closing socket:\n{}'.format(e))
        print('Socket closed...')

if __name__ == "__main__":
    client = Client()
    client.run()