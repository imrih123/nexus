from allcode import ServerComm
from serverCode import ServerFiles
from serverCode import DB
from serverCode import serverProtocol
import queue
import os
from allcode import settingSer
import threading


def handle_nitur_msgs(nitur_queue):
    """
    call the func by the opcode
    :param nitur_queue: the nitur queue
    """
    while True:
        ip, message = nitur_queue.get()
        opcode, name_of_file = serverProtocol.serverProtocol.unpack(message)
        nitur_commands[opcode]([name_of_file[0], ip])


def file_added(params):
    """
    add the file to the list of file and send to every one
    :params: list of params
    """
    name_of_file, ip = params[0], params[1]
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        # add ip to torrent file
        files_obj.add_ip_to_torrent(name_of_file, ip)
        # add to the count of clients of the file
        open_files[name_of_file][1] = open_files[name_of_file][1]+1
        string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(open_files)
        # send update to every client
        general_comm.sendall(string_of_open_files)
    else:
        # send to the client to delete the file from nitur
        delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
        nitur_comm.send(delete_file_msg, ip)


def file_deleted(params):
    """
    delete the client ip from the torrent and change the list of files
    :param params: list of params
    """
    name_of_file, ip = params[0], params[1]
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        # delete the ip from the torrent
        files_obj.delete_ip_from_torrent(name_of_file, ip)
        if name_of_file in open_files:
            # delete client from the count of open clients
            open_files[name_of_file][1] = max(0, open_files[name_of_file][1]-1)
        string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(open_files)
        # send every client update
        general_comm.sendall(string_of_open_files)


def file_changed(params):
    """
    delete the client ip from the torrent and change the list of files
    :param params: list of params
    """
    name_of_file, ip = params[0], params[1]
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(name_of_file)
    torrents_db.closeDb()
    if have_torrent:
        # delete ip from torrent
        files_obj.delete_ip_from_torrent(name_of_file, ip)
        if name_of_file in open_files:
            # remove the client from the count of clients
            open_files[name_of_file][1] = max(0, open_files[name_of_file][1]-1)
        string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(open_files)
        # send every client
        general_comm.sendall(string_of_open_files)
    # send to the client to delete the file from the nitur file
    delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
    nitur_comm.send(delete_file_msg, ip)


def file_name_changed(params):
    """
    send the client to delete the file from nitur
    :param params: list of params
    """
    name_of_file, ip = params[0], params[1]
    delete_file_msg = serverProtocol.serverProtocol.Delete_file_from_folder(name_of_file)
    nitur_comm.send(delete_file_msg, ip)


def handle_general_msgs(general_queue):
    """
    call the func by the opcode
    :param general_queue: the queue connect to the general comm
    """
    while True:
        ip, message = general_queue.get()
        opcode, params = serverProtocol.serverProtocol.unpack(message)
        params.append(ip)
        general_commands[opcode](params)


def send_list_of_files(params):
    """
    send the list of files to the client
    :param params:list of params
    :return:
    """
    ip = params[0]
    message = serverProtocol.serverProtocol.Create_string_of_list(open_files)
    general_comm.send(message, ip)


def send_torrent(params):
    """
    send the torrent file to the client
    :param params: list of params
    """
    file_name = params[0]
    ip = params[1]
    # get the torrent file
    torrent_file = files_obj.get_torrent_file(file_name)
    header = serverProtocol.serverProtocol.Response_for_torrent_request(file_name)
    general_comm.send_file(torrent_file, header, ip)


def create_uplaod_socket(params):
    """
    create the upload comm and send to the client the info
    :param params: list of params
    :return:
    """
    path_of_file, ip = params[0], params[1]
    file_name = os.path.basename(path_of_file)
    torrents_db = DB.DBClass()
    have_torrent = torrents_db.have_torrent(file_name)
    torrents_db.closeDb()
    if not have_torrent:
        upload_queue = queue.Queue()
        # get port from the generator
        port = next(unused_ports)
        upload_comm = ServerComm.ServerComm(port, upload_queue, 8)
        threading.Thread(target=handle_upload_file, args=(upload_queue, upload_comm)).start()
    else:
        # file already exists with that name
        port = -1
    # send to the client the port
    response = serverProtocol.serverProtocol.Response_for_upload_request(path_of_file, port)
    general_comm.send(response, ip)


def handle_upload_file(upload_queue, upload_comm):
    """
    get the data from the queue and create the torrent file
    :param upload_queue: the queue of the file
    :param upload_comm: the comm
    """
    torrents_db = DB.DBClass()
    ip, message = upload_queue.get()
    file_name, data = message[1], message[2]
    if not torrents_db.have_torrent(file_name):
        # create the torrent file
        files_obj.create_torrent_file(data, file_name)
        # add the torrent file to the db
        torrents_db.add_torrent(file_name)
        # add the file name to the list of file
        open_files[file_name] = [len(data), 0]
        string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(open_files)
        general_comm.sendall(string_of_open_files)
    torrents_db.closeDb()
    response = serverProtocol.serverProtocol.Response_for_upload()
    upload_comm.send(response, ip)
    upload_comm.close_socket()


def handle_disconnect_nitur(params):
    """
    if client disconnect delete all the files that he had and send to everyone
    :param params: list of params
    :return:
    """
    ip = params[1]
    # all the names that the ip had
    list_of_names = files_obj.handdle_disconnect(ip)
    for name in list_of_names:
        if name in open_files:
            open_files[name][1] = max(0, open_files[name][1] - 1)
    string_of_open_files = serverProtocol.serverProtocol.Create_string_of_list(open_files)
    general_comm.sendall(string_of_open_files)


def create_open_files():
    """
    create the list of file with all the files from the torrent file

    """
    files_name = os.listdir(settingSer.PATH_OF_TORRENTS_FOLDER)
    for name in files_name:
        name = name[:-5]
        torrent = files_obj.get_torrent_file(name, string=False)
        open_files[name] = [torrent["len of file"], 0]


if __name__ == '__main__':
    # all the opcodes and funcs
    general_commands = {"01": send_torrent, "02": create_uplaod_socket, "03": send_list_of_files}
    # all the opcodes and funcs
    nitur_commands = {"-1": handle_disconnect_nitur, "01": file_added, "02": file_deleted, "03": file_changed, "05": file_name_changed}

    # the files object
    files_obj = ServerFiles.Server_files(settingSer.PATH_OF_TORRENTS_FOLDER)

    open_files = {}
    create_open_files()

    unused_ports = (x for x in range(2000, 2500))

    general_queue = queue.Queue()
    nitur_queue = queue.Queue()

    # the general comm
    general_comm = ServerComm.ServerComm(1500, general_queue, 6)
    # the nitur comm
    nitur_comm = ServerComm.ServerComm(1600, nitur_queue, 2)

    # start the handle 
    threading.Thread(target=handle_general_msgs, args=(general_queue,)).start()
    threading.Thread(target=handle_nitur_msgs, args=(nitur_queue,)).start()

