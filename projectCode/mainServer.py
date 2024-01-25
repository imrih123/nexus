import Encryption_Decryption
import ServerComm
import ServerFiles
import DB
import serverProtocol
import queue
import os
import setting
import threading


def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        ip, message = general_queue.get()
        opcode, params = serverProtocol.serverProtocol.unpack(message)
        params.append(ip)
        general_commands[opcode](params)


def handle_upload_file(upload_queue, upload_comm):
    """

    :param queue:
    :return:
    """
    torrents_db = DB.DBClass()
    ip, message = upload_queue.get()
    file_name, data = message[1], message[2]
    if not torrents_db.have_torrent(file_name):

        files_obj.create_torrent_file(data, file_name)
        torrents_db.add_torrent(file_name)
    response = serverProtocol.serverProtocol.Response_for_upload()
    upload_comm.send(response, ip)
    upload_comm.close_socket()


def create_uplaod_socket(params):
    """

    :param path_of_file:
    :param ip:
    :return:
    """
    path_of_file, ip = params[0], params[1]
    file_name = os.path.basename(path_of_file)
    torrents_db = DB.DBClass()
    if not torrents_db.have_torrent(file_name):
        upload_queue = queue.Queue()
        port = next(unused_ports)
        upload_comm = ServerComm.ServerComm(port, upload_queue, 8)
        threading.Thread(target=handle_upload_file, args=(upload_queue, upload_comm)).start()
        response = serverProtocol.serverProtocol.Response_for_upload_request(path_of_file, port)
        general_comm.send(response, ip)



if __name__ == '__main__':
    general_commands = {"01": create_uplaod_socket}
    nitur_commands = {}

    list_of_open_files = []
    unused_ports = (x for x in range(2000, 2500))

    general_queue = queue.Queue()
    nitur_queue = queue.Queue()

    general_comm = ServerComm.ServerComm(1500, general_queue, 4)
    nitur_comm = ServerComm.ServerComm(1600, nitur_queue, 2)

    threading.Thread(target=handle_general_msgs, args=(general_queue,)).start()

    files_obj = ServerFiles.Server_files(setting.PATH_OF_TORRENTS_FOLDER)
