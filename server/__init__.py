import socket
import threading
import json
from util import int_to_bytes


class Server:

    PORT = 5000
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDRESS = (SERVER, PORT)
    FORMAT = "utf-8"
    DELIMITER = "@"

    def __init__(self):

        self.players = {}
        self.clients = {}
        self.server = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)

    def run(self):
        self.server.bind(Server.ADDRESS)

        print("server is working on " + Server.SERVER)

        self.server.listen()
        while True:
            conn, addr = self.server.accept()
            print(addr)
            get_username = """["NAME"]"""
            conn.send(int_to_bytes(len(get_username)))
            conn.send(get_username.encode(self.FORMAT))

            name = conn.recv(1024).decode(self.FORMAT)
            player = {"name": name, "address": addr[0], "port": addr[1]}
            handle = name + "@" + addr[0] + ":" + str(addr[1])
            self.players[handle] = player
            self.clients[handle] = conn
            print(player)

            thread = threading.Thread(target=self._handle,
                                      args=(handle,))
            thread.start()
            print(f"Active connections: {len(self.clients)}")

    def _handle(self, handle):
        # print(f"New connection: {addr}")
        connected = True
        while handle in self.clients:
            print(handle)
            payload = json.dumps(self.players).encode(self.FORMAT)
            payload_size = int_to_bytes(len(payload))
            self.broadcast(payload_size)
            self.broadcast(payload)
            import time
            time.sleep(1)

    def broadcast(self, message):
        disconnected = []
        for handle, client in self.clients.items():
            try:
                client.sendall(message)
            except (ConnectionAbortedError, ConnectionResetError):
                print(self.players[handle]["name"] + " has left the server!")
                self.players.pop(handle)
                disconnected.append(handle)
        for handle in disconnected:
            self.clients.pop(handle).close()


if __name__ == "__main__":
    server = Server()
    server.run()
