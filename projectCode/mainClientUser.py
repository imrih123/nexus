import clientProtocol
import ClientFiles
import ClientComm
import ServerComm
import Encryption_Decryption
import queue
import threading
import os
import setting

def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        message = general_queue.get()
        opcode, params = clientProtocol.clientProtocol.unpack(message)
        general_commands[opcode](params)


def create_socket_upload(params):
    """

    :param port:
    :param name_of_file:
    :return:
    """
    port, path_of_file = int(params[0]), params[1]
    file_name = os.path.basename(path_of_file)
    upload_comm = ClientComm.Clientcomm(server_ip, queue, port, 8)
    data = ClientFiles.client_files.get_part_of_file(path_of_file, -1)
    header = clientProtocol.clientProtocol.Upload_file(file_name)
    upload_comm.send_file(data, header)
    

if __name__ == '__main__':
    server_ip = setting.SERVER_IP
    path_to_file = fr"C:\Users\talmid\Downloads\cat.jpg"
    general_commands = {"02": create_socket_upload}
    gui_commands = {}
    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    general_comm = ClientComm.Clientcomm(server_ip, general_queue, 1500, 4)
    threading.Thread(target=handle_general_msgs, args=(general_queue, )).start()
    while general_comm.crypt_object is None:
        continue
    ask_torrent = clientProtocol.clientProtocol.Request_torrent_file(path_to_file)
    general_comm.send(ask_torrent)

