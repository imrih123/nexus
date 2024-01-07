import hashlib
import socket
import random

name_of_file = input("enter name of file: ")

number_part_hash = {}
number_part_data = {}
pic = bytearray()
hash_object = hashlib.sha256()
client_socket = socket.socket()
client_socket.connect(("127.0.0.1", 1450))
len_name_of_file = str(len(name_of_file)).zfill(2)
client_socket.send((len_name_of_file + name_of_file).encode())
number_of_parts = int(client_socket.recv(2).decode())

parts = [i for i in range(number_of_parts)]
f = open(fr"C:\Users\talmid\Downloads\\{name_of_file}", 'wb')
while parts:
    current_part = random.choice(parts)
    msg = f"{str(current_part).zfill(3)}{name_of_file}"
    client_socket.send(f"{str(len(msg)).zfill(2)}01{msg}".encode())
    len_message = client_socket.recv(4).decode()
    print(len_message)
    len_message = int(len_message)
    a = len_message
    number_part = client_socket.recv(3).decode()
    data_part = bytearray()
    while len_message >= 1024:
        data_part += client_socket.recv(1024)
        len_message -= 1024
    if len_message != 0:
        data_part += client_socket.recv(len_message)
    while len(data_part) < 4096:
        break
        # add data

    hash_object.update(data_part)
    full_part_hash = hash_object.hexdigest()
    number_part_hash[current_part] = full_part_hash
    f.seek(current_part * 4096)
    f.write(data_part)
    #if current_part is min(parts):
        # pic.extend(data_part)
    # else:
        # number_part_data[current_part] = data_part
    parts.remove(current_part)

f.close()

# number_part_data = dict(sorted(number_part_data.items()))
# for value in number_part_data.values():
    # pic.extend(value)
