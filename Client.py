import socket
import threading
from utils import (PORT, IP, BUFFER_SIZE, compute_checksum, headers, get_message,
                     get_checksum, get_window_size, get_ack)
from datetime import datetime
import traceback
class Client:
    def __init__(self):
        self.running = True
        self.nickname = input("Escolha seu apelido: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))

        self.sequence_number = 0
        self.sequence_number_lock = threading.Lock()
        self.window_size = 5
        self.last_ack_received = 0

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def increment_sequence_number(self):
        with self.sequence_number_lock:
            self.sequence_number += 1

    def receive(self):
        while self.running:
            try:
                # receives message and prints it
                data = self.client.recv(BUFFER_SIZE)
                message = get_message(data)
                self.window_size = get_window_size(data)
                self.last_ack_received = get_ack(data)
                if message == 'NICK': # saves the nickname
                    self.client.send(headers({"message": self.nickname}))
                else:
                    print(f"{datetime.now().strftime('%H:%M')} {message}\n")
            except:
                print("Ocorreu um erro!")
                self.client.close()
                break

    def write(self):
        # if message is 'sair', exits the server, else sends message to server
        while self.running:
            try:
                # print("sq: ", self.sequence_number)
                # print("ack: ", self.last_ack_received)
                if self.sequence_number - self.last_ack_received < self.window_size:
                    message = '{}: {}'.format(self.nickname, input('> '))
                    self.increment_sequence_number()
                    data = {"sequence_number": self.sequence_number, "message": message}
                    json_data = headers(data)
                    self.client.send(json_data)
            except: 
                print(traceback.print_exc())

if __name__ == '__main__':
    client = Client()


