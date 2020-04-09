from Server import *
from Client import *
from Config import *
import sys

def Main():
    print("Starting client and server...")
    server = Server()
    client = Client()
    try:
        server.run()
        print("Server started...")
        client.run()
        print("Client started...")
    except Exception as e:
        print("Error starting client and server: {}".format(e))


if __name__ == "__main__":
    Main()