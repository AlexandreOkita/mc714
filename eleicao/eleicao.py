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

        if message == "ping":
            return pb2.MessageResponse(**{'message': "pong", 'received': True})

        if message.startswith("eleicao"):
            num = message.split(",")[1]
            self.process.eleicao_ocorrendo = True
            if num < self.process.my_number:
                self.process.send_message_to_next(f"eleicao,{self.process.my_number}")
                return pb2.MessageResponse(**{'message': f"continuado", "received": True})
            if num > self.process.my_number:
                self.process.send_message_to_next(f"eleicao,{num}")
                return pb2.MessageResponse(**{'message': f"continuado", "received": True})
            self.process.coordenador = self.process.my_number
            for address in self.process.other_numbers:
                try:
                    c.UnaryClient(address, '5000').send_message(f"OK,{self.process.my_number},{address}")
                except:
                    continue
            self.process.eleicao_ocorrendo = False
            print("Novo coordenador:", self.process.coordenador)
            return pb2.MessageResponse(**{'message': f"eleicao encerrada", "received": True})

        if message.startswith("OK"):
            self.process.coordenador = message.split(',')[1]
            print("Novo coordenador:", self.process.coordenador)
            self.process.eleicao_ocorrendo = False

        
class Process:
    def __init__(self):
        self.my_number = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        self.other_numbers = []
        self.coordenador = ""
        self.eleicao_ocorrendo = False        

    def get_other_processes(self):
        with open("/home/ubuntu/mc714/hosts") as f:
            all_numbers = [line.strip() for line in f.readlines()]
        self.coordenador = max(all_numbers)
        self.other_numbers = (all_numbers[all_numbers.index(self.my_number):]+all_numbers[:all_numbers.index(self.my_number)])[1:]
    
    def send_message_to_next(self, message):
        for succ in self.other_numbers:
            try:
                print("Trying to send message to", succ)
                return c.UnaryClient(succ, '5000').send_message(message)
            except:
                time.sleep(2)
        print("no other node to send message")
    
    def send_message_to_coordinator(self, message):
        return c.UnaryClient(self.coordenador, '5000').send_message(message)


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
    print("Current coordinator:", process.coordenador)

    # Recebe mensagem de eleição
    Thread(target=serve, args=('5000', process,)).start()
    #pinga e inicia eleicao
    while True:
        #nao eh o coordenador
        if process.my_number != process.coordenador:
            try:
                print("Response:\n", process.send_message_to_coordinator("ping"), sep='')
                time.sleep(10)
            except Exception as e:
                print("Iniciando eleicao")
                process.eleicao_ocorrendo = True
                process.send_message_to_next(f"eleicao,{process.my_number}")
                while process.eleicao_ocorrendo:
                   time.sleep(1)