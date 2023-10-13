import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers,
                    get_message, get_checksum, unpack_data)
import traceback
class Server:
    nicknames = []
    clients = []
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()

        self.receive()
        
    def broadcast(self, data):
        # generates checksum and sends it to every connected client
        data = unpack_data(data)
        message = data['message']
        checksum = compute_checksum(message)
        message_with_checksum = "{} {}".format(message, str(checksum)).encode("ascii")
        data = {'message':message} # dictionary format for easier transfer
        json_data = headers(data) # function that encodes the dictionary to json/ascii
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
                        self.broadcast(data)
                else:
                    print("Soma de verificação inválida.")
            except Exception as e:
                print(traceback.print_exc())
                self.remove_client(client)
                break

    def receive(self):
        # connects client and broadcasts their connection
        while True:
              
            client, address = self.server.accept()
            print("Conectado com {}".format(str(address)))

            data = {"message":"NICK"}
            json_data = headers(data)
            client.send(json_data)
            data = client.recv(BUFFER_SIZE)
            nickname = get_message(data) # TODO: VERIFY CHECKSUM
            self.nicknames.append(nickname)
            self.clients.append(client)


            print("{} conectou.".format(nickname))
            
            data = {"message":f"Bem vindo {nickname}! Digite \"sair\" para desconectar.\n"}
            json_data = headers(data)
            client.send(json_data)
            
            data = {"message":f"{nickname} entrou no chat!\n"}
            json_data = headers(data)
            self.broadcast(json_data)


            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

    def remove_client(self, client):
        # disconnects client from server
        client.send(headers({'message':"Até logo!"}))
        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        nickname = self.nicknames[index]
        self.broadcast(headers({"message":f"{nickname} saiu."}))
        self.nicknames.remove(nickname)

if __name__ == '__main__':
    server = Server()