from clientCode import clientProtocol
from clientCode import ClientFiles
from clientCode import ClientComm
from clientCode.p2pProcess import _build_com
from allcode import Encryption_Decryption
import queue
import threading
import os
from allcode import settingCli
import json
import multiprocessing
import wx
from clientCode import graphics
from pubsub import pub
import time


def handle_general_msgs(general_queue):
    """
    call the func by the opcode
    :param general_queue: the queue of the general comm
    """
    while True:
        message = general_queue.get()
        if type(message) == tuple:
            p2p_download(message)
        else:
            opcode, params = clientProtocol.clientProtocol.unpack(message)
            general_commands[opcode](params)


def p2p_download(params):
    """
    download the file using p2p connection
    :param params:list of the params
    """

    json_string = params[3]
    list_of_processes = []
    torrnet_dict = json.loads(json_string)
    file_name = torrnet_dict["file name"]
    len_of_part = int(torrnet_dict["part len"])
    file_queue = multiprocessing.Queue()
    comms = {}
    open_ips_dict = torrnet_dict['open ip']
    number_of_pieces = torrnet_dict['number of pieces']
    # create list of pieces
    list_of_pieces = [0 for _ in range(number_of_pieces)]
    wx.CallAfter(pub.sendMessage, "start progress", total_parts=number_of_pieces,
                 name_of_file=file_name)
    # start a thread to get the parts from the queue
    threading.Thread(target=_get_parts_from_queue, args=(comms, torrnet_dict['hash of pieces'], torrnet_dict['full hash'], file_queue, file_name, list_of_pieces, len_of_part,)).start()

    # for each ip create comm
    for ip in open_ips_dict:
        ip_queue = multiprocessing.Queue()
        comms[ip] = [ip_queue, 0]
        # start a process for each ip
        p = multiprocessing.Process(target=_build_com, args=(ip_queue, file_queue, ip, file_name,len_of_part))
        p.start()
        list_of_processes.append(p)
        # get the index of the next part
        index = _find_first(list_of_pieces, -1, -1)
        ip_queue.put(index)


def _get_parts_from_queue(comms, list_of_hash, full_data_hash, file_queue, file_name, list_of_pieces, len_of_part):
    """

    get the parts of the file from the queue check the hash and update the graphics
    :param comms: list of comm
    :param list_of_hash: list of parts hash
    :param full_data_hash: the full hash of the data
    :param file_queue:the queue connect to the every process
    :param file_name: the name of the file
    :param list_of_pieces: the list of each piece status
    """

    global abort
    build_file = queue.Queue()
    path = f"{settingCli.PATH_TO_SAVE_FILES}\{file_name}"
    first_time = time.time()
    # thread that build the file
    threading.Thread(target=_build_file, args=(build_file, path, len_of_part)).start()
    while not abort:
        ip, file_name, number_of_part, data = file_queue.get()
        # not a time out
        if data != -1:
            hash_part = Encryption_Decryption.AES_encryption.hash(data)
            # check hash
            # bad hash
            if list_of_hash[number_of_part] != str(hash_part):
                # disconnect
                comms[ip][0].put(-1)
                del comms[ip]
                # if last comm
                if len(comms) == 0:
                    print("Fail - hash are not the same ")
                    break
            # good hash
            else:
                # add the part to the file
                build_file.put((data, number_of_part))
                # let the graphics know
                wx.CallAfter(pub.sendMessage, "new part")

                # not the first part anymore
                # get the index of the next part to download
                index = _find_first(list_of_pieces, -1, number_of_part)
                # all the part are done
                if index == -1:
                    # end the func that build the file
                    break
                # ask for the next part
                comms[ip][0].put(index)
        # couldn't find part
        else:
            # after 3 try's
            if comms[ip][1] == 2:
                # close the comm
                comms[ip][0].put(-1)
                del comms[ip]
                if len(comms) == 0:
                    print("Fail - to many try's, closed socket")
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
    print(f"the time to download is {time.time() - first_time}")
    wx.CallAfter(pub.sendMessage, "close progress")
    # close all the sockets
    for ip in comms:
        comms[ip][0].put(-1)
    abort = False
    build_file.put((0, -1))
    data = ClientFiles.client_files.get_part_of_file(path, -1, -1)
    full_hash = Encryption_Decryption.AES_encryption.hash(data)
    # check the full hash
    if full_data_hash == str(full_hash):
        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)


def _build_file(build_queue, path, len_of_part):
    """P
    open the file, build the file with data from the queue and close the file
    :param build_queue: the queue
    :param path: the path
    """
    f = open(path, 'wb')
    while True:
        data, number_of_part = build_queue.get()
        # -1 = last part
        if number_of_part is -1:
            break
        f.seek(number_of_part*len_of_part)
        f.write(data)
    f.close()


def _find_first(list_of_pieces, cant_recv, number_found=-1):
    """

    :param list_of_pieces: the list of the status
    :param cant_recv: if part fail, dont ask for him again
    :param number_found: the number of part that was found
    :return:
    """
    # if a number was found
    if number_found != -1:
        # change the status of the part
        list_of_pieces[number_found] = -1
    # if all the parts found return -1
    if list_of_pieces.count(-1) == len(list_of_pieces):
        index = -1
    else:
        if cant_recv != -1:
            # if a part wasn't found change the status
            list_of_pieces[cant_recv] -= 1
        # find new part to ask
        number_list = [n for n in list_of_pieces if n >= 0 and n != cant_recv]
        # if no other part was found
        if len(number_list) == 0:
            # delete the comm
            index = -2
        else:
            # ask for the part with the min number of working clients on him
            min_number = min(number_list)
            index = list_of_pieces.index(min_number)
            # change the status
            list_of_pieces[index] += 1
    return index


def create_socket_upload(params):
    """
    create a comm and upload the file
    :param params:
    :return:
    """
    port, path_of_file = int(params[0]), params[1]
    if port != -1:
        upload_queue = queue.Queue()
        file_name = os.path.basename(path_of_file)
        # create comm
        upload_comm = ClientComm.Clientcomm(server_ip, upload_queue, port, 8)
        data = ClientFiles.client_files.get_part_of_file(path_of_file, -1, -1)
        header = clientProtocol.clientProtocol.upload_file(file_name)
        # send the data
        upload_comm.send_file(data, header)


def get_response_server(params):
    """

    :param params:
    :return:
    """
    response, path = params[0], params[1]
    if response == "111":
        data = ClientFiles.client_files.get_part_of_file(path, -1, -1)
        file_name = os.path.basename(path)
        ClientFiles.client_files.save_file(settingCli.NITUR_FOLDER, file_name, data)
        wx.CallAfter(pub.sendMessage, "after upload")
    else:
        # if file already exists
        wx.CallAfter(pub.sendMessage, "file exists")


def create_list_of_files(params):
    """
    call a func in the graphics to update the list of file
    :param params: list of files
    """
    params = [params]
    list_of_files = [[item.split(',') for item in sublist] for sublist in params]
    wx.CallAfter(pub.sendMessage, "new list", new_file_list=list_of_files[0])


def get_message_from_gui(gui_queue):
    """
    send to the server the command the user did
    :param gui_queue: the queue connect the qui to the logic
    """
    global abort
    while True:
        order, path = gui_queue.get()
        if order == "download":
            message = clientProtocol.clientProtocol.request_torrent_file(path)
        elif order == "upload":
            message = clientProtocol.clientProtocol.request_upload(path)
        elif order == "abort":
            abort = True
            # close the loop of the download
            continue
        else:
            continue
        general_comm.send(message)


if __name__ == '__main__':
    server_ip = settingCli.SERVER_IP
    # all the general opcodes and funcs
    general_commands = {"01": p2p_download, "02": create_socket_upload, "03": create_list_of_files
        , "04": get_response_server}

    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    abort = False

    # create the general comm
    general_comm = ClientComm.Clientcomm(server_ip, general_queue, 1500, 6)
    # start the handles
    threading.Thread(target=handle_general_msgs, args=(general_queue, )).start()
    threading.Thread(target=get_message_from_gui, args=(gui_queue,)).start()
    # start the main thread of the graphics
    app = wx.App()
    frame = graphics.MyFrame(None, "nexus", gui_queue, logo_path=settingCli.IMAGES_PATH)
    app.MainLoop()



