from Config import *
import os, sys, socket

class Client:
    def __init__(self):
        self.UDP_server_IP = "127.0.0.1"
        self.UDP_server_Port = 5005
        self.invocation = AT_LEAST_ONCE
        