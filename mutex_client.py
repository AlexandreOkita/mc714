import client as c

if __name__ == '__main__':
    client = c.UnaryClient('localhost', 50051)
    response = client.send_message('Hello, world!')
    print(response)