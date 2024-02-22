import clientProtocol
import ClientComm
import settingCli


def _build_com(main_queue, file_queue, ip, file_name):
    """

    :param main_queue:
    :param file_queue:
    :param ip:
    :param file_name:
    :return:
    """
    comm = ClientComm.Clientcomm(ip, file_queue, settingCli.P2P_PORT, 4)
    while True:
        index = main_queue.get()
        if index == -1:
            comm.close_socket()
        else:
            request_part = clientProtocol.clientProtocol.request_part_file(file_name, index)
            comm.send(request_part)


