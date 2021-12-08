import client as c

if __name__ == '__main__':
    with open("/home/ubuntu/mc714/mutex_server_ip") as f:
            server = f.readlines()[0].strip()
    client = c.UnaryClient('server', 5000)
    response = client.send_message('banana')
    print(response)