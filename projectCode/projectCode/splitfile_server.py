import socket
import os
import math
path = r"T:\public\יב\imri\projectCode\\files\\"
# F:\cyber\cat.jpg"
server_socket = socket.socket()
server_socket.bind(("0.0.0.0", 1450))
server_socket.listen(3)
client_socket, ip = server_socket.accept()


len_of_message = int(client_socket.recv(2).decode())
name_of_file = client_socket.recv(len_of_message).decode()
number_of_parts = math.ceil(os.path.getsize(path+name_of_file)/4096)
client_socket.send(str(number_of_parts).zfill(2).encode())
while True:
    len_of_message = client_socket.recv(2).decode()
    opcode = client_socket.recv(2).decode()
    if opcode == "00":
        pass
    if opcode == "01":
        message = client_socket.recv(int(len_of_message)).decode()
        print(message)
        number_of_part = int(message[:3])
        name_of_file = message[3:]
        print(number_of_part, name_of_file)
        with open(f"{path}{name_of_file}", 'rb') as f:
            f.seek(number_of_part * 4096)
            data = f.read(4096)
            data_len = str(len(data)).zfill(4)
            number_of_part = str(number_of_part).zfill(3)
            header = f"{data_len}{number_of_part}"
            print(header)
            client_socket.send(header.encode() + data)


        # file_size = len(data)
        # print(f"The file '{path}' has {file_size} bytes.")

    # file_size = os.path.getsize(path)
    # print(f"The file '{path}' has {file_size} bytes.")




