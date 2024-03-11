from serverCode import DB
from serverCode import serverProtocol
from allcode import ServerComm


def handle_upload_file(upload_queue, files_obj, port, update_list_queue):
    """

    :param upload_queue:
    :param upload_comm:
    :param general_comm:
    :param open_files:
    :param files_obj:
    :return:
    """

    upload_comm = ServerComm.ServerComm(port, upload_queue, 8)
    torrents_db = DB.DBClass()
    ip, message = upload_queue.get()
    file_name, data = message[1], message[2]
    if not torrents_db.have_torrent(file_name):
        # create the torrent file
        files_obj.create_torrent_file(data, file_name)
        # add the torrent file to the db
        torrents_db.add_torrent(file_name)
        # add the file name to the list of file
        update_list_queue.put((file_name, len(data)))
    else:
        temp = f"temp{port}"
        files_obj.create_torrent_file(data, temp)
        test = files_obj.get_torrent_file(temp)
        if test == files_obj.get_torrent_file(file_name):
            files_obj.add_ip_to_torrent(file_name, ip)
            update_list_queue.put((file_name, -1))
    torrents_db.closeDb()
    response = serverProtocol.serverProtocol.Response_for_upload()
    upload_comm.send(response, ip)
    upload_comm.close_socket()