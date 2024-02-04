import clientProtocol
import ClientFiles
import ClientComm
import ServerComm
import Encryption_Decryption
import queue
import threading
import os
import settingCli
import time
import json
import math


def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        message = general_queue.get()
        print(message, " handle general msgs client")
        opcode, params = clientProtocol.clientProtocol.unpack(message)
        general_commands[opcode](params)


def p2p_download(params):
    """

    :param params:
    :return:
    """
    json_string = params[0]
    torrnet_dict = json.loads(json_string)
    print(f"\n\n{torrnet_dict}")
    file_name = torrnet_dict["file name"]
    file_queue = queue.Queue()
    build_file = queue.Queue()
    threading.Thread(target=_build_file, args=(build_file, file_name,)).start()
    list_of_pieces = [0 for _ in range(torrnet_dict['number of pieces'])]
    comms = {}

    for ip in torrnet_dict['open ip']:
        comm = ClientComm.Clientcomm(ip, file_queue, 3333, 4)
        comms[ip] = [comm, 0]
        index = _find_first(list_of_pieces, -1, -1)
        request_part = clientProtocol.clientProtocol.request_part_file(file_name, index)
        comm.send(request_part)

    while True:
        print(1)
        ip, file_name, number_of_part, data = file_queue.get()
        print(2)
        # found part
        if data != -1:
            if torrnet_dict["hash of pieces"][number_of_part] != Encryption_Decryption.AES_encryption.hash(data):
                comms[ip][0].close_socket()
                del comms[ip]
                if len(comms) == 0:
                    print("Fail")
                    # send to gui
                    break
            else:
                build_file.put(data, number_of_part)
                index = _find_first(list_of_pieces, -1, number_of_part)
                if index == -1:
                    print("good")
                    # send to gui
                    break
                request_part = clientProtocol.clientProtocol.request_part_file(file_name, index)
                comms[ip][0].send(request_part)
        # couldn't find part
        else:
            # to many try's
            if comms[ip][1] == 2:
                comms[ip][0].close_socket()
                del comms[ip]
                if len(comms) == 0:
                    print("Fail")
                    # send to gui
                    break
            else:
                # add a try
                comms[ip][1] += 1
                index = _find_first(list_of_pieces, number_of_part)
                # could find last part
                if index == -2:
                    comms[ip][0].close_socket()
                    del comms[ip]
                    if len(comms) == 0:
                        print("Fail")
                        # send to gui
                        break
                else:
                    request_part = clientProtocol.clientProtocol.request_part_file(file_name, index)
                    comms[ip][0].send(request_part)


def _build_file(build_queue, file_name):
    """

    :return:
    """
    data, number_of_part = build_queue.get()
    with open(f"{settingCli.PATH_TO_SAVE_FILES}\{file_name}", 'a') as f:
        f.seek(number_of_part*4096)
        f.write(data)


def _find_first(list_of_pieces, cant_recv, number_found=-1):
    """

    :param list_of_pieces:
    :param number_of_clients:
    :return:
    -1 = found all pieces
    -2 = cant find other piece

    """
    if number_found != -1:
        list_of_pieces[number_found] = -1
    if list_of_pieces.count(-1) == len(list_of_pieces):
        index = -1
    else:
        if cant_recv != -1:
            list_of_pieces[cant_recv] -= 1
        number_list = [n for n in list_of_pieces if n >= 0 and n != cant_recv]
        if len(number_list) == 0:
            index = -2
        else:
            min_number = min(number_list)
            index = list_of_pieces.index(min_number)
            list_of_pieces[index] += 1
    return index


def create_socket_upload(params):
    """

    :param port:
    :param name_of_file:
    :return:
    """
    port, path_of_file = int(params[0]), params[1]
    upload_queue = queue.Queue()
    file_name = os.path.basename(path_of_file)
    upload_comm = ClientComm.Clientcomm(server_ip, upload_queue, port, 8)
    data = ClientFiles.client_files.get_part_of_file(path_of_file, -1)
    header = clientProtocol.clientProtocol.upload_file(file_name)
    upload_comm.send_file(data, header)
    response = upload_queue.get()
    if response == "011":
        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)


if __name__ == '__main__':
    server_ip = settingCli.SERVER_IP
    path_to_file = fr"C:\Users\talmid\Downloads\dog.jpg"
    general_commands = {"01": p2p_download, "02": create_socket_upload}
    gui_commands = {}
    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    general_comm = ClientComm.Clientcomm(server_ip, general_queue, 1500, 4)
    threading.Thread(target=handle_general_msgs, args=(general_queue, )).start()
    opcode = input(": ")
    if opcode == "upload":
        request_upload_file = clientProtocol.clientProtocol.request_upload(path_to_file)
        general_comm.send(request_upload_file)

    # time.sleep(3)
    elif opcode == "download":
        request_torrent_file = clientProtocol.clientProtocol.request_torrent_file("dog.jpg")
        general_comm.send(request_torrent_file)

