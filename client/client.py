import socket
import queue
from config import SERVER_ADDRESS
from util import int_from_bytes
import json
import threading


class Client:
    FORMAT = "utf-8"

    def __init__(self, server=SERVER_ADDRESS):
        self.client = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.client.connect(server)
        self.message_queue = queue.Queue()

    def start(self, username):
        while True:
            try:
                received_message = self.receive_message()
                if isinstance(received_message, list):
                    message = username
                    self.client.send(message.encode(self.FORMAT))
                else:
                    self.message_queue.put(received_message)
            except:
                # TODO: fix concurrent access to client socket
                print("error")
                break

    def disconnect(self):
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()

    def receive_message(self):
        length = int_from_bytes(self.client.recv(1))
        payload = self.client.recv(length).decode(self.FORMAT)
        return json.loads(payload)
