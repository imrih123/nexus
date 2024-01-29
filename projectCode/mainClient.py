import clientProtocol
import ClientComm
import ClientFiles
import ServerComm
import Encryption_Decryption
import monitoring
import queue
import settingCli
import threading


def handle_p2p_msgs(Server_upload_queue):
    """

    :param Server_upload_queue:
    :return:
    """
    while True:
        ip, message = Server_upload_queue.get()
        opcode, params = clientProtocol.clientProtocol.unpack(message)
        params.append(ip)
        upload_server_commands[opcode](params)


def send_part_of_file(params):
    """

    :param params:
    :return:
    """
    file_part, file_name, ip = params[0], params[1], params[2]
    data_of_part = ClientFiles.client_files. \
        get_part_of_file(f"{settingCli.NITUR_FOLDER}\\{file_name}", file_part)
    header = clientProtocol.clientProtocol.Send_file_part(file_name, file_part)
    upload_server.sendfile(header, data_of_part, ip)


def handle_nitur_msgs(nitur_queue):
    """

    :param nitur_queue:
    :param nitur:
    :return:
    """
    while True:
        message = nitur_queue.get()
        opcode, file_name = clientProtocol.clientProtocol.unpack(message)
        nitur_commands[opcode](file_name)


def add_file(file_name):
    """

    :param file_name:
    :return:
    """
    update_in_nitur = clientProtocol.clientProtocol.Added_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def delete_file(file_name):
    """

    :param file_name:
    :return:
    """
    update_in_nitur = clientProtocol.clientProtocol.removed_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def change_file(file_name):
    """

    :param file_name:
    :return:
    """
    update_in_nitur = clientProtocol.clientProtocol.changed_file_nitur(file_name)
    nitur_comm.send(update_in_nitur)


def handle_nitur_comm_msgs(nitur_comm_queue):
    """

    :param nitur_comm_queue:
    :return:
    """
    while True:
        message = nitur_comm_queue.get()
        opcode, file_name = clientProtocol.clientProtocol.unpack(message)
        if opcode == "03":
            ClientFiles.client_files.delete_file(fr"{settingCli.NITUR_FOLDER}\\{file_name}")


if __name__ == '__main__':
    nitur_queue = queue.Queue()
    nitur = monitoring.monitoring(settingCli.NITUR_FOLDER, nitur_queue)

    nitur_comm_queue = queue.Queue()
    nitur_comm = ClientComm.Clientcomm(settingCli.SERVER_IP, nitur_comm_queue, settingCli.NITUR_PORT, 2)

    upload_server_queue = queue.Queue()
    upload_server = ServerComm.ServerComm(settingCli.P2P_UPLOAD_PORT, upload_server_queue, 4)

    nitur_commands = {}
    upload_server_commands = {}

    threading.Thread(target=handle_nitur_comm_msgs, args=(nitur_comm_queue,)).start()
    threading.Thread(target=handle_nitur_msgs, args=(nitur_queue,)).start()
    threading.Thread(target=handle_p2p_msgs, args=(upload_server_queue,)).start()

