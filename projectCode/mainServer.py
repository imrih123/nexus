import Encryption_Decryption
import ServerComm
import ServerFiles
import DB
import serverProtocol
import queue
import os
import settingSer
import threading


def handle_nitur_msgs(nitur_queue):
    """

    :param nitur_queue:
    :return:
    """
    while True:
        ip, message = nitur_queue.get()
        print(message, "handle nitur msg server")
        opcode, name_of_file = serverProtocol.serverProtocol.unpack(message)
        nitur_commands[opcode](name_of_file[0], ip)


def file_added(name_of_file, ip):
    """

    :param name_of_file:
    :param ip:
    :return:
    """
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        need_to_send = files_obj.add_ip_to_torrent(name_of_file, ip)
        if need_to_send:
            list_of_open_files.append(name_of_file)
            string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(list_of_open_files)
            general_comm.sendall(string_of_open_files)
    else:
        delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
        nitur_comm.send(delete_file_msg, ip)



def file_deleted(name_of_file, ip):
    """

    :param name_of_file:
    :param ip:
    :return:
    """
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        need_to_send = files_obj.delete_ip_from_torrent(name_of_file, ip)
        if need_to_send:
            if name_of_file in list_of_open_files:
                list_of_open_files.remove(name_of_file)
            string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(list_of_open_files)
            general_comm.sendall(string_of_open_files)


def file_changed(name_of_file, ip):
    """

    :param name_of_file:
    :param ip:
    :return:
    """
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        need_to_send = files_obj.delete_ip_from_torrent(name_of_file, ip)
        if need_to_send:
            if name_of_file in list_of_open_files:
                list_of_open_files.remove(name_of_file)
            string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(list_of_open_files)
            general_comm.sendall(string_of_open_files)
    delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
    nitur_comm.send(delete_file_msg, ip)


def file_name_changed(name_of_file, ip):
    """

    :param name_of_file:
    :param ip:
    :return:
    """
    delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
    nitur_comm.send(delete_file_msg, ip)


def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        ip, message = general_queue.get()
        print(message, " handle general msgs server")
        opcode, params = serverProtocol.serverProtocol.unpack(message)
        params.append(ip)
        general_commands[opcode](params)


def send_torrent(params):
    """

    :param params:
    :return:
    """
    file_name = params[0]
    ip = params[1]
    torrent_file = files_obj.get_torrent_file(file_name)
    header = serverProtocol.serverProtocol.Response_for_torrent_request(file_name)
    general_comm.send_file(torrent_file, header, ip)


def create_uplaod_socket(params):
    """

    :param path_of_file:
    :param ip:
    :return:
    """
    path_of_file, ip = params[0], params[1]
    file_name = os.path.basename(path_of_file)
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(file_name)
    torrents_db.closeDb()
    if not have_torrent:
        upload_queue = queue.Queue()
        port = next(unused_ports)
        upload_comm = ServerComm.ServerComm(port, upload_queue, 8)
        threading.Thread(target=handle_upload_file, args=(upload_queue, upload_comm)).start()
        response = serverProtocol.serverProtocol.Response_for_upload_request(path_of_file, port)
        general_comm.send(response, ip)


def handle_upload_file(upload_queue, upload_comm):
    """

    :param queue:
    :return:
    """
    torrents_db = DB.DBClass()
    ip, message = upload_queue.get()
    file_name, data = message[1], message[2]
    print(torrents_db.have_torrent(file_name))
    if not torrents_db.have_torrent(file_name):
        files_obj.create_torrent_file(data, file_name)
        torrents_db.add_torrent(file_name)
    torrents_db.closeDb()
    response = serverProtocol.serverProtocol.Response_for_upload()
    upload_comm.send(response, ip)
    upload_comm.close_socket()


if __name__ == '__main__':
    general_commands = {"01": send_torrent, "02": create_uplaod_socket}
    nitur_commands = {"01": file_added, "02": file_deleted, "03": file_changed, "05": file_name_changed}

    list_of_open_files = []
    unused_ports = (x for x in range(2000, 2500))

    general_queue = queue.Queue()
    nitur_queue = queue.Queue()

    general_comm = ServerComm.ServerComm(1500, general_queue, 6)
    nitur_comm = ServerComm.ServerComm(1600, nitur_queue, 2)

    threading.Thread(target=handle_general_msgs, args=(general_queue,)).start()
    threading.Thread(target=handle_nitur_msgs, args=(nitur_queue,)).start()

    files_obj = ServerFiles.Server_files(settingSer.PATH_OF_TORRENTS_FOLDER)
