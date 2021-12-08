import client as c

if __name__ == '__main__':
    with open("/home/ubuntu/mc714/mutex_server_ip") as f:
            server = f.readlines()[0].strip()
    print("Sending to IP:", server)
    message = input("Enter message: ")
    while message != "" or message != "exit":
        client = c.UnaryClient(server, 5000)
        response = client.send_message(message)
        print(response)
        print()