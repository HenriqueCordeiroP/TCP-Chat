import socket
import threading
from utils import PORT, IP, BUFFER_SIZE, compute_checksum

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
                message = self.client.recv(BUFFER_SIZE).decode('ascii')
                if message == 'NICK': # saves the nickname
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    try:
                        checksum = int(message.split()[-1])
                        message = ' '.join(message.split()[:-1])
                    except ValueError:
                        pass
                    print(message)
            except:
                print("Ocorreu um erro!")
                self.running = False
                self.client.close()
                break

    def write(self):
        # if message is 'sair', exists the server, else sends message to server
        while self.running:
            message = '{}: {}'.format(self.nickname, input(''))
            if message == 'sair':
                self.running = False
                self.client_socket.close()
            else:
                checksum = compute_checksum(message)
                message = "{} {}".format(message, str(checksum))
                self.client.send(message.encode('ascii'))

if __name__ == '__main__':
    client = Client()