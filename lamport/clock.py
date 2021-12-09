import grpc
import client as c
from concurrent import futures
from threading import Thread
import time
import test_pb2_grpc as pb2_grpc
import test_pb2 as pb2
import os
import urllib.request

class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, process):
        self.process = process
        pass
    
    def GetServerResponse(self, request, context):
        message = request.message
        print("Received message from client: ", message)
        self.process.clock = max(int(message.split(",")[1]), self.process.clock) + 1
        print("Clock value: ", self.process.clock)
        return pb2.Response(**{'message': str(self.process.clock), "received": True})

        
class Process:
    def __init__(self):
        self.my_number = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        self.other_numbers = []
        self.eleicao_ocorrendo = False
        self.clock = 0

    def get_other_processes(self):
        with open("/home/ubuntu/mc714/hosts") as f:
            all_numbers = [line.strip() for line in f.readlines()]
        self.other_numbers = (all_numbers[all_numbers.index(self.my_number):]+all_numbers[:all_numbers.index(self.my_number)])[1:]
        
    def send_message(self, host, message):
        return c.UnaryClient(host, '5000').send_message(message)
    
    def show_menu(self):
        print("Available hosts:")
        for ind, host in enumerate(self.other_numbers):
            print(f"{ind}: {host}")
        print("==================================================")
        print()


def serve(port, process):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UnaryServicer_to_server(UnaryService(process), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    process = Process()
    process.get_other_processes()
    print("My number:", process.my_number)

    # Recebe mensagem de eleição
    Thread(target=serve, args=('5000', process,)).start()
    process.show_menu()
    host = input("Choose a host: ")
    host = process.other_numbers[int(host)]
    message = input("Now enter a message: ")
    while message != "" or message != "exit":
        client = c.UnaryClient(host, 5000)
        response = client.send_message(message+","+str(process.clock))
        print("New clock:", response)
        process.clock = int(response)
        print()
        message = input("Enter message: ")
        