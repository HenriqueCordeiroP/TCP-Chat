import socket
import threading
from utils import PORT, IP, BUFFER_SIZE, compute_checksum, headers, get_message, get_checksum, unpack_data
import traceback
import time

class Server:
    nicknames = []
    clients = []

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()

        self.acknowledgements = {}
        self.message_timeout = 30
        self.nack_messages = {}
        self.sequence_number = 0
        self.sequence_number_lock = threading.Lock()

        self.receive()

    def increment_sequence_number(self):
        with self.sequence_number_lock:
            self.sequence_number += 1

    def broadcast(self, data):
        # sends message to every connected client
        data = unpack_data(data)
        message = data['message'] # dictionary format for easier transfer
        json_data = headers({'message': message})   # function that encodes the dictionary to json/ascii
        for client in self.clients:
            client.send(json_data)

    def handle(self, client):
        # receives message, handles checksum and broadcasts the message
        while True:
            try:
                data = client.recv(BUFFER_SIZE)
                received_checksum = get_checksum(data)
                message = get_message(data)
                if received_checksum == compute_checksum(message):
                    if message == 'sair':
                        self.remove_client(client)
                        break
                    else:
                        self.increment_sequence_number()
                        data = unpack_data(data)
                        data["sequence_number"] = self.sequence_number
                        data = headers(data)

                         # add to nack dictonary. if message is sent, it will be removed
                        self.nack_messages[message] = (client, data)

                         # create and start timer thread 
                        acknowledgment_timer = threading.Thread(target=self.timer, args=(client, data))
                        acknowledgment_timer.start()
                        self.broadcast(data)
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

            client.send(headers({"message": "NICK"}))
            data = client.recv(BUFFER_SIZE)
            received_checksum = get_checksum(data)
            nickname = get_message(data)
            if received_checksum != compute_checksum(nickname):
                print("Ocorreu um erro no envio do apelido.")
            else:
                self.nicknames.append(nickname)
                self.clients.append(client)
                print("{} conectou.".format(nickname))
                client.send(headers({"message": f"Bem vindo {nickname}! Digite \"sair\" para desconectar.\n"}))
                self.broadcast(headers({"message": f"{nickname} entrou no chat!\n"}))
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()

    def remove_client(self, client):
        # disconnects client from server
        client.send(headers({'message': "Até logo!"}))
        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        nickname = self.nicknames[index]
        self.broadcast(headers({"message": f"{nickname} saiu."}))
        self.nicknames.remove(nickname)

if __name__ == '__main__':
    server = Server()

