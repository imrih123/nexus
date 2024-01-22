import clientProtocol
import ClientFiles
import ClientComm
import ServerComm
import Encryption_Decryption
import queue
import threading
import os


def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        opcode, params = clientProtocol.clientProtocol.unpack(general_queue.get())
        general_commands[opcode](params)


def create_socket_upload(port, path_of_file):
    """

    :param port:
    :param name_of_file:
    :return:
    """
    file_name = os.path.basename(path_of_file)
    upload_comm = ClientComm.Clientcomm(server_ip, queue, port, 4)
    data = ClientFiles.client_files.get_part_of_file(path_of_file, -1)
    header = clientProtocol.clientProtocol.Upload_file(file_name)
    upload_comm.send_file(data, header)
    

if __name__ == '__main__':
    server_ip = "168.182.4.98"
    general_commands = {"02" : create_socket_upload}
    gui_commands = {}
    general_queue = queue.Queue()
    gui_queue = queue.Queue()
    list_of_open_file = []
    general_comm = ClientComm.Clientcomm(server_ip, queue, 1500, 4)
    threading.Thread(target=handle_general_msgs).start()

