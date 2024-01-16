import abc
import threading
import socket
import Encryption_Decryption

class Clientcomm(object):
    def __init__(self, server_ip, message_queue, port, zfill_number):
        """

        :param server_ip:
        :param message_queue:
        :param port:
        :param zfill_number:
        """
        self.server_ip = server_ip
        self.message_queue = message_queue
        self.port = port
        self.zfill_number = zfill_number
        self.client_Scoket = None
        self.crypt_object = None
        self.is_socket_open = True
        threading.Thread(target=self._recv_messages()).start()

    def _recv_messages(self):
        """

        :return:
        """
        self.client_socket = socket.socket()
        self.client_socket.connect((self.server_ip, self.port))
        self._xchange_key()
        while self.is_socket_open:
            re

    def _recv_file(self, opcode, file_name, file_length):
        """

        :param file_name:
        :param file_length:
        :return:
        """
        data_part = bytearray()
        while file_length >= 1024:
            data_part += self.client_socket.recv(1024)
            file_length -= 1024
        if file_length != 0:
            data_part += self.client_socket.recv(file_length)
        self.message_queue.put(f"{opcode}{file_name}$%${file_length}$%${data_part})")

    def _xchange_key(self):
        """

        :return:
        """
        b, B = Encryption_Decryption.AES_encryption.get_dif_Num()
        len_of_B = str(len(B)).zfill(4)
        opcode = ""
        len_of_key = 0
        try:
            self.client_Scoket.send(f"00{len_of_B}{B}".encode())
        except Exception as e:
            print(e)

        try:
            opcode = self.client_Scoket.recv(2).decode()
        except Exception as e:
            print(e)
        if opcode is "00":
            try:
                len_of_key = self.client_Scoket.recv(4).decode()
            except Exception as e:
                print(e)
            try:
                A = int(self.client_Scoket.recv(int(len_of_key)).decode())
            except Exception as e:
                print(e)
            else:
                cryptobject = Encryption_Decryption.AES_encryption.set_key(A, b)
                # exchange keys and create cryptObject
                self.cryptobject = cryptobject

    def send(self, message):
        """

        :param message:
        :return:
        """
        if self.cryptobject is not None and self.is_socket_open:
            encrypt_msg = self.cryptobject.encrypt(message)
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            self.client_socket.send(len_encrypt_msg + encrypt_msg)

    def close_socket(self):
        """

        :return:
        """
        self.is_socket_open = False
