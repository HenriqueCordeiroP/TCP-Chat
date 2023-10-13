import socket
import threading
from utils import PORT, IP, BUFFER_SIZE, compute_checksum
import traceback

class Server:
    nicknames = []
    clients = []
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen()

        self.receive()
        
    def broadcast(self, message):
        # generates checksum and sends it to every connected client
        checksum = compute_checksum(message)
        message_with_checksum = "{} {}".format(message, str(checksum)).encode("ascii")
        for client in self.clients:
            client.send(message_with_checksum)

    def handle(self, client):
        # receives message, handles checksum and broadcasts the message
        while True:
            try:
                message = client.recv(BUFFER_SIZE)
                received_checksum = int(message.split()[-1])
                message = ' '.join(message.decode('ascii').split()[:-1])
                if received_checksum == compute_checksum(message):
                    if message.split()[-1] == 'sair':
                        self.remove_client(client)
                        break
                    else:
                        self.broadcast(message.encode('ascii'))
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


            client.send('NICK'.encode('ascii'))
            nickname = client.recv(BUFFER_SIZE).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)


            print("{} conectou.".format(nickname))
            client.send('Bem vindo {}! Digite "sair" para desconetar.\n '.format(nickname).encode('ascii'))
            self.broadcast("{} entrou no chat!".format(nickname).encode('ascii'))


            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

    def remove_client(self, client):
        # disconnects client from server
        client.send("Adeus!".encode('ascii'))
        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        nickname = self.nicknames[index]
        self.broadcast('{} saiu.'.format(nickname).encode('ascii'))
        self.nicknames.remove(nickname)

if __name__ == '__main__':
    server = Server()