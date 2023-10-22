import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers,
                     get_message, get_checksum, unpack_data, get_sequence_number)
import traceback
import time

class Server:
    nicknames = []
    clients = []
    sequence_numbers = []
    
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()

        self.acknowledgements = {}
        self.message_timeout = 30
        self.window_size = 5
        self.nack_messages = {}

        self.window_size_lock = threading.Lock()
        self.sequence_number_lock = threading.Lock()

        self.receive()

    def increment_sequence_number(self, index):
        with self.sequence_number_lock:
            current_number = self.sequence_numbers[index]
            current_number += 1
            self.sequence_numbers[index] =  current_number

    def increment_window_size(self):
        with self.window_size_lock:
            self.window_size += 1

    def decrement_window_size(self):
        with self.window_size_lock:
            self.window_size -= 1

    def broadcast(self, data):
        # sends message to every connected client
        try:
            for client in self.clients:
                client.send(data)
            self.increment_window_size()
        except:
            print(traceback.print_exc())

    def handle(self, client):
        # receives message, handles checksum and broadcasts the message
        while True:
            try:
                data = client.recv(BUFFER_SIZE)
                received_checksum = get_checksum(data)
                message = get_message(data)
                received_sequence_number = get_sequence_number(data)
                self.decrement_window_size()

                index = self.clients.index(client)
                self.increment_sequence_number(index)

                client_ack = self.sequence_numbers[index] + 1

                if received_checksum == compute_checksum(message):
                    if self.sequence_numbers[index] == received_sequence_number:
                        unpacked = unpack_data(data)
                        unpacked['window_size'] = self.window_size
                        unpacked['ack'] = client_ack
                        data = headers(unpacked)
                         # add to nack dictonary. if message is sent, it will be removed
                        self.nack_messages[message] = (client, data)

                         # create and start timer thread 
                        acknowledgment_timer = threading.Thread(target=self.timer, args=(client, data))
                        acknowledgment_timer.start()
                        self.broadcast(data)
                    else:
                        print("Número de sequência incorreto.")
                else:
                    print("Soma de verificação inválida.")
            except:
                print(traceback.print_exc())
                self.remove_client(client)
                break

    def timer(self, client, data):
        time.sleep(self.message_timeout)
        if not self.ack_ok(data):
            # handle timeout
            print("Timeout. Trying again...")
            self.broadcast(data)

    def ack_ok(self, data):
        message = get_message(data)
        if message in self.nack_messages:
            del self.nack_messages[message]
            return True
        return False

    def receive(self):
        # connects client and broadcasts their connection
        while True:
            client, address = self.server.accept()
            print("Conectado com {}".format(str(address)))

            client.send(headers({"message": "NICK", "window_size": self.window_size, "ack": 1}))
            data = client.recv(BUFFER_SIZE)
            received_checksum = get_checksum(data)
            nickname = get_message(data)
            if received_checksum != compute_checksum(nickname):
                print("Ocorreu um erro no envio do apelido.")
            else:
                self.nicknames.append(nickname)
                self.clients.append(client)
                self.sequence_numbers.append(0)
                print("{} conectou.".format(nickname))
                client.send(headers({"message": f"Bem vindo {nickname}!", "window_size": self.window_size, "ack": 1}))
                self.broadcast(headers({"message": f"{nickname} entrou no chat!\n", "window_size": self.window_size, "ack": 1}))
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()

    def remove_client(self, client):
        # disconnects client from server
        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        nickname = self.nicknames[index]
        self.broadcast(headers({"message": f"{nickname} saiu.", "window_size": self.window_size, "ack": 1}))
        self.nicknames.remove(nickname)

if __name__ == '__main__':
    server = Server()

