from serverCode import DB
from allcode import ServerComm


def handle_upload_file(upload_queue, files_obj, port, update_list_queue, path_of_file):
    """
    open a server and recv a file from the client
    :param upload_queue: the queue from the comm
    :param files_obj: files object
    :param port: port of server
    :param update_list_queue: queue to the logic
    -1 same file already exist, -2 same name already exists
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
        update_list_queue.put((file_name, ip, path_of_file, len(data)))
    else:
        temp = f"temp{port}"
        files_obj.create_torrent_file(data, temp)

        # check if the file is the same as the origin file, create a torrent and compare if they are the same
        # (without the same name and open ip header
        temp_torrent = files_obj.get_torrent_file(temp, False)
        temp_torrent = list(temp_torrent.values())[2:]

        files_obj.delete_temp(temp)

        origin_torrent = files_obj.get_torrent_file(file_name, False)
        origin_torrent = list(origin_torrent.values())[2:]

        if temp_torrent == origin_torrent:
            files_obj.add_ip_to_torrent(file_name, ip)
            update_list_queue.put((file_name, ip, path_of_file, -1))
        else:
            update_list_queue.put((file_name, ip, path_of_file, -2))
    torrents_db.closeDb()
    upload_comm.close_socket()
