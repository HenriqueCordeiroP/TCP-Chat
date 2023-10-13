import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers,
                    get_message, get_checksum)
class Client:
    def __init__(self):
        self.running = True
        self.nickname = input("Escolha seu apelido: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))
        
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def receive(self):
        while self.running:
            try:
                # receives message and prints it
                data = self.client.recv(BUFFER_SIZE)
                message = get_message(data)
                if message == 'NICK': # saves the nickname
                    self.client.send(headers({"message":self.nickname}))
                else:
                    print(message)
            except:
                print("Ocorreu um erro!")
                self.running = False
                self.client.close()
                break

    def write(self):
        # if message is 'sair', exits the server, else sends message to server
        while self.running:
            message = '{}: {}'.format(self.nickname, input(''))
            if message == 'sair':
                self.running = False
                self.client_socket.close()
            else:
                data = {"message":message}
                json_data = headers(data)
                self.client.send(json_data)

if __name__ == '__main__':
    client = Client()