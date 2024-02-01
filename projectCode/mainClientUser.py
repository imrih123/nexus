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

    # with open(fr"C:\Users\talmid\Downloads\cat.jpg", 'rb') as f:
    #     data = f.read()
    # list_of_hash = []
    # for i in range(math.ceil(len(data) / 4096)):
    #     data_part = data[i * 4096:(i + 1) * 4096]
    #     list_of_hash.append(str(Encryption_Decryption.AES_encryption.hash(data_part)))
    # full_hash = str(Encryption_Decryption.AES_encryption.hash(data))
    #
    # for i in range(len(list_of_hash)):
    #     if torrnet_dict["hash of pieces"][i] == list_of_hash[i]:
    #         print("good part", i)
    #     else:
    #         print("bad part", i)
    # print(full_hash == torrnet_dict["full hash"])


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
    header = clientProtocol.clientProtocol.Upload_file(file_name)
    upload_comm.send_file(data, header)
    response = upload_queue.get()
    if response == "011":
        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)


if __name__ == '__main__':
    server_ip = settingCli.SERVER_IP
    path_to_file = fr"C:\Users\talmid\Downloads\yotam.jpg"
    general_commands = {"01": p2p_download, "02": create_socket_upload}
    gui_commands = {}
    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    general_comm = ClientComm.Clientcomm(server_ip, general_queue, 1500, 4)
    threading.Thread(target=handle_general_msgs, args=(general_queue, )).start()

    request_upload_file = clientProtocol.clientProtocol.Request_upload(path_to_file)
    general_comm.send(request_upload_file)

    #time.sleep(3)

    # request_torrent_file = clientProtocol.clientProtocol.Request_torrent_file("cat.jpg")
    # general_comm.send(request_torrent_file)

