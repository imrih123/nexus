from clientCode import clientProtocol
from clientCode import ClientComm
from allcode import settingCli


def _build_com(main_queue, file_queue, ip, file_name, len_of_part):
    """

    :param main_queue: the queue connect to the logic
    :param file_queue: the queue that recv the files
    :param ip: the ip of the server
    :param file_name:the name of the file
    """
    comm = ClientComm.Clientcomm(ip, file_queue, settingCli.P2P_PORT, 4)
    while True:
        index = main_queue.get()
        # close the socket
        if index == -1:
            comm.close_socket()
        else:
            request_part = clientProtocol.clientProtocol.request_part_file(file_name, index, len_of_part)
            comm.send(request_part)


