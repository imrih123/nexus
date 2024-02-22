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
import multiprocessing
from p2pProcess import _build_com
import wx
import graphics
from pubsub import pub


def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        message = general_queue.get()
        print(message, "handle general msgs ")
        if type(message) == tuple:
            p2p_download(message)
        else:
            opcode, params = clientProtocol.clientProtocol.unpack(message)
            general_commands[opcode](params)


def p2p_download(params):
    """
    :param params:
    :return:
    """
    json_string = params[3]
    list_of_processes = []
    torrnet_dict = json.loads(json_string)
    file_name = torrnet_dict["file name"]
    # file_queue = queue.Queue()
    file_queue = multiprocessing.Queue()
    comms = {}
    open_ips_dict = torrnet_dict['open ip']
    number_of_pieces = torrnet_dict['number of pieces']
    list_of_pieces = [0 for _ in range(number_of_pieces)]
    threading.Thread(target=_get_parts_from_queue, args=(comms, torrnet_dict['hash of pieces'], torrnet_dict['full hash'], file_queue, file_name, list_of_pieces,)).start()
    for ip in open_ips_dict:
        ip_queue = multiprocessing.Queue()
        comms[ip] = [ip_queue, 0]
        p = multiprocessing.Process(target=_build_com, args=(ip_queue, file_queue, ip, file_name,))
        p.start()
        list_of_processes.append(p)
        index = _find_first(list_of_pieces, -1, -1)
        ip_queue.put(index)

    for p in list_of_processes:
        p.join()


def _get_parts_from_queue(comms, list_of_hash, full_data_hash,file_queue, file_name, list_of_pieces):
    """

    :param comms:
    :param list_of_hash:
    :param full_data_hash:
    :param file_queue:
    :param file_name:
    :param list_of_pieces:
    :return:
    """

    test_time = time.time()
    build_file = queue.Queue()
    path = f"{settingCli.PATH_TO_SAVE_FILES}\{file_name}"
    threading.Thread(target=_build_file, args=(build_file, path,)).start()

    while True:
        ip, file_name, number_of_part, data = file_queue.get()
        # print("the sender is: ", ip)
        # found part
        if data != -1:
            hash_part = Encryption_Decryption.AES_encryption.hash(data)
            if list_of_hash[number_of_part] != str(hash_part):
                comms[ip][0].put(-1)
                del comms[ip]
                if len(comms) == 0:
                    print("Fail - hash are not the same ")
                    # send to gui
                    break
            else:
                build_file.put((data, number_of_part))
                index = _find_first(list_of_pieces, -1, number_of_part)
                if index == -1:
                    build_file.put((0, -1))
                    data = ClientFiles.client_files.get_part_of_file(path, -1)
                    full_hash = Encryption_Decryption.AES_encryption.hash(data)
                    if full_data_hash == str(full_hash):
                        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)
                        print("the time of the download is ", time.time()-test_time)
                        # close all the sockets
                        for ip in comms:
                            comms[ip][0].put(-1)
                    else:
                        print("full hash - bad ")
                    # send to gui
                    break
                comms[ip][0].put(index)
        # couldn't find part
        else:
            # to many try's
            if comms[ip][1] == 2:
                comms[ip][0].put(-1)
                del comms[ip]
                if len(comms) == 0:
                    print("Fail - to many try's, closed socket")
                    # send to gui
                    break
            else:
                # add a try
                comms[ip][1] += 1
                index = _find_first(list_of_pieces, number_of_part)
                # could find last part
                if index == -2:
                    comms[ip][0].put(-1)
                    del comms[ip]
                    if len(comms) == 0:
                        print("Fail - last part wasn't found")
                        # send to gui
                        break
                else:
                    comms[ip][0].put(index)


def _build_file(build_queue, path):
    """

    :return:
    """
    f = open(path, 'wb')
    while True:
        data, number_of_part = build_queue.get()
        if number_of_part is -1:
            break
        f.seek(number_of_part*settingCli.BLOCKSIZE)
        f.write(data)
    f.close()


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
    if response == "111":
        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)


def create_list_of_files(params):
    """

    :param params:
    :return:
    """
    params = [params]
    print(params)
    list_of_files = [[item.split(',') for item in sublist] for sublist in params]
    print(list_of_files[0])
    wx.CallAfter(pub.sendMessage, "new list", new_file_list=list_of_files[0])


def get_message_from_gui(gui_queue):
    """

    :param gui_queue:
    :return:
    """
    while True:
        order, path = gui_queue.get()
        if order == "download":
            message = clientProtocol.clientProtocol.request_torrent_file(path)
        elif order == "upload":
            message = clientProtocol.clientProtocol.request_upload(path)
        else:
            print("wrong order", order)
            continue
        print(message)
        general_comm.send(message)


if __name__ == '__main__':
    server_ip = settingCli.SERVER_IP
    path_to_file = fr"C:\Users\talmid\Downloads\test3.zip"
    general_commands = {"01": p2p_download, "02": create_socket_upload, "03": create_list_of_files}
    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    general_comm = ClientComm.Clientcomm(server_ip, general_queue, 1500, 6)
    threading.Thread(target=handle_general_msgs, args=(general_queue, )).start()
    threading.Thread(target=get_message_from_gui, args=(gui_queue,)).start()
    app = wx.App()
    frame = graphics.MyFrame(None, "nexus", gui_queue)
    app.MainLoop()



