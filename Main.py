from Server import *
from Client import *
from Config import *
import sys

def Main():
    print("Starting client...")
    client = Client()
    try:
        client.run()
        print("Client started...")
    except Exception as e:
        print("Error starting client: {}".format(e))


if __name__ == "__main__":
    Main()