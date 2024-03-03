from clientCode import clientProtocol
from clientCode import ClientComm
from clientCode import ClientFiles
from allcode import ServerComm
from clientCode import monitoring
import queue
from allcode import settingCli
import threading


def handle_p2p_msgs(Server_upload_queue):
    """
    calls the func by the opcode
    :param Server_upload_queue: the queue of the p2p messages
    """
    while True:
        ip, message = Server_upload_queue.get()
        opcode, params = clientProtocol.clientProtocol.unpack(message)
        params.append(ip)
        upload_server_commands[opcode](params)


def send_part_of_file(params):
    """
    send the part of the file
    :param params: the params
    """
    file_part, file_name, ip = int(params[0]), params[1], params[2]
    data_of_part = ClientFiles.client_files. \
        get_part_of_file(f"{settingCli.NITUR_FOLDER}\\{file_name}", file_part)
    header = clientProtocol.clientProtocol.send_file_part(file_name, file_part)
    upload_server.send_file(data_of_part, header, ip)


def handle_nitur_msgs(nitur_queue):
    """
    calls the func by the opcode
    :param nitur_queue: the queue of the nitur messages
    """
    while True:
        opcode, file_name = nitur_queue.get()
        nitur_commands[opcode](file_name)


def add_file(file_name):
    """
    send to the server that a file been added to the nitur
    :param file_name: the file name
    """
    update_in_nitur = clientProtocol.clientProtocol.added_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def delete_file(file_name):
    """
    send to the server that a file been deleted from the nitur
    :param file_name: the name
    """
    update_in_nitur = clientProtocol.clientProtocol.removed_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def change_file(file_name):
    """
    send to the server that a file been changed in the nitur
    :param file_name: the name
    """
    update_in_nitur = clientProtocol.clientProtocol.changed_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def change_file_name(file_name):
    """
    send to the server that a file name been changed in the nitur
    :param file_name: the name
    """
    update_in_nitur = clientProtocol.clientProtocol.changed_file_name_new_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def handle_nitur_comm_msgs(nitur_comm_queue):
    """
    calls the func by the opcode
    :param nitur_comm_queue: the queue of the messages from the server nitur comm
    """
    while True:
        message = nitur_comm_queue.get()
        opcode, file_name = clientProtocol.clientProtocol.unpack(message)
        if opcode == "03":
            ClientFiles.client_files.delete_file(fr"{settingCli.NITUR_FOLDER}\\{file_name[0]}")


if __name__ == '__main__':
    # create the nitur object
    nitur_queue = queue.Queue()
    nitur = monitoring.monitoring(settingCli.NITUR_FOLDER, nitur_queue)

    # create server for a p2p comm
    upload_server_queue = queue.Queue()
    upload_server = ServerComm.ServerComm(settingCli.P2P_PORT, upload_server_queue, 4)

    # create client comm for the nitur messages
    nitur_comm_queue = queue.Queue()
    nitur_comm = ClientComm.Clientcomm(settingCli.SERVER_IP, nitur_comm_queue, settingCli.NITUR_PORT, 2)

    # all the nitur commands and funcs
    nitur_commands = {"01": add_file, "02": delete_file, "03": change_file, "05": change_file_name}

    upload_server_commands = {"01": send_part_of_file}

    # start as a thread the handles
    threading.Thread(target=handle_nitur_comm_msgs, args=(nitur_comm_queue,)).start()
    threading.Thread(target=handle_nitur_msgs, args=(nitur_queue,)).start()
    threading.Thread(target=handle_p2p_msgs, args=(upload_server_queue,)).start()

