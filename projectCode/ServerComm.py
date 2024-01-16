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
        self.server_socket = None
        self.is_socket_open = True
        threading.Thread(target=self._recv_messages()).start()

    def _recv_messages(self):
        """

        :return:
        """
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(3)
        while self.is_socket_open:
            rlist, wlist, xlist = select.select([self.server_socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [])
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    threading.Thread(target=self._xchange_key).start()

                # else:

    def _xchange_key(self):
        """

        :return:
        """
        (new_client, addr) = self.server_socket.accept()
        a, A = Encryption_Decryption.AES_encryption.get_dif_Num()
        opcode = ""
        len_of_key = 0
        len_of_A = str(len(A)).zfill(4)
        try:
            opcode = new_client.recv(2).decode()
        except Exception as e:
            print(e)
        if opcode is "00":
            try:
                len_of_key = new_client.recv(4).decode()
            except Exception as e:
                print(e)
            try:
                B = int(new_client.recv(int(len_of_key)).decode())
            except Exception as e:
                print(e)
            else:
                cryptobject = Encryption_Decryption.AES_encryption.set_key(B,a)
                # exchange keys and create cryptObject
                self.open_clients[new_client] = [addr[0], cryptobject]
            try:
                new_client.send(f"00{len_of_A}{A}".encode())
            except Exception as e:
                print(e)

    def _find_socket_by_ip(self, find_ip):
        """

        :param find_ip:
        :return:
        """
        for socket, ip in self.open_clients:
            if ip == find_ip:
                return socket

    def send(self, message, ip):
        """

        :param message:
        :param ip:
        :return:
        """
        current_socket = self._find_socket_by_ip(ip)
        if current_socket is not None:
            encrypt_msg = self.open_clients[current_socket][1].eecrypt(message.encode())
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            current_socket.send(len_encrypt_msg+encrypt_msg)

    def sendall(self, message):
        """

        :param message:
        :return:
        """
        for ip in self.open_clients.keys():
            self.send(message, ip)

    def _recv_file(self, ip, len_message, file):
        """

        :return:
        """
        current_socket = self._find_socket_by_ip(ip)
        data_part = bytearray()
        while len_message >= 1024:
            data_part += current_socket.recv(1024)
            len_message -= 1024
        if len_message != 0:
            data_part += current_socket.recv(len_message)

    def close_socket(self):
        """

        :return:
        """
        self.is_socket_open = False
