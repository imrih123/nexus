import socket
import select
import threading
import Encryption_Decryption

class ServerComm(object):
    def __init__(self, port, message_queue, zfill_number):
        """

        :param port:
        :param message_queue:
        :param zfill_number:
        """
        self.port = port
        self.message_queue = message_queue
        self.zfill_number = zfill_number
        self.open_clients = {}

    def _Recv_messages(self):
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", 1500))
        self.server_socket.listen(3)
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [])
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    threading.Thread(target=self._Xchange_key).start()

    def _Xchange_key(self):
        """

        :return:
        """
        (new_client, addr) = self.server_socket.accept()
        A = Encryption_Decryption.get_key()
        try:
            new_client.send(f"00{A}".encode())
        except Exception as e:
            print(e)
        try:
            len_of key = new_client.recv(2).decode()
        except Exception as e:
            print(e)
        # exchange keys and create cryptObject
        self.open_clients[new_client] = [addr[0], cryptobject]

    def _find_socket_by_ip(self, find_ip):
        """

        :param find_ip:
        :return:
        """
        for socket, ip in self.open_clients:
            if ip == find_ip:
                return socket
        return None

    def send
