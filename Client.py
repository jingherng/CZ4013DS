from Config import *
import os, sys, socket, logging

class Client:
    def __init__(self):
        self.UDP_server_IP = "127.0.0.1"
        self.UDP_server_Port = 5005
        self.invocation = [AT_LEAST_ONCE, AT_MOST_ONCE]
        logging.basicConfig(filename='client.log',level=logging.DEBUG)
    
    def run(self):
        logging.info('Starting client socket...')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as e:
            logging.error("Failed to create client socket: {}".format(e))
            sys.exit()

        HOST = 'localhost'
        PORT = 7777
        
        while True:
            msg = input('Enter message to send:')
            msg = bytes(msg, 'utf-8')
            try:
                self.sock.sendto(msg, (HOST, PORT))
            except socket.error as e:
                logging.error('Error sending message: {}'.format(e))

            
            try:
                data, address = self.sock.recvfrom(4096)
                logging.info('Server reply from {}: {}'.format(address, data))

            except socket.error as e:
                logging.error('Error receiving message: {}'.format(e))

if __name__ == "__main__":
    client = Client()
    client.run()