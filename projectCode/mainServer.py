import Encryption_Decryption
import ServerComm
import ServerFiles
import DB
import serverProtocol
import queue
import os

def handle_general_msgs(general_queue):
    """

    :param general_queue:
    :return:
    """
    while True:
        opcode, params = serverProtocol.serverProtocol.unpack(general_queue.get())
        general_commands[opcode](params)



def handle_upload_file(file_name):

def create_uplaod_socket(path_of_file, ):

    file_name = os.path.basename(path_of_file)
    torrents_db = DB.DBClass()
    if not torrents_db.have_torrent(file_name):
        upload_queue = queue.Queue()
        port = yield unused_ports
        upload_comm = ServerComm.ServerComm(port, upload_queue, 8)




if __name__ == '__main__':
    general_commands = {}
    nitur_commands = {}

    list_of_open_files = []
    unused_ports = (x for x in range(2000, 2500))

    general_queue = queue.Queue()
    nitur_queue = queue.Queue()

    general_comm = ServerComm.ServerComm(1500, general_queue, 4)
    nitur_comm = ServerComm.ServerComm(1600, nitur_queue, 2)

