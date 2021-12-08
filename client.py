import grpc
import test_pb2_grpc as pb2_grpc
import test_pb2 as pb2

class UnaryClient(object):

    def __init__(self, host, port):
        self.host = host
        self.server_port = port
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port)
        )
        self.stub = pb2_grpc.UnaryStub(channel=self.channel)

    def send_message(self, message):
        """
        Client function to call the rpc for GetServerResponse
        """
        message = pb2.Message(message=message)
        print(f'Sending message: {message.message}')
        return self.stub.GetServerResponse(message)

if __name__ == '__main__':
    client = UnaryClient('localhost', 50051)
    my_input = ''
    while my_input != 'exit':
        my_input = input('Enter a message: ')
        response = client.send_message(my_input)
        print(f'Received message: {response.message}')
        print()