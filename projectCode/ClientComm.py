import abc
import threading
import socket
import Encryption_Decryption
import sys
import queue
import time
import clientProtocol


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
        self.client_socket = None
        self.crypt_object = None
        self.is_socket_open = True
        threading.Thread(target=self._recv_messages).start()

    def _recv_messages(self):
        """
        :return:
        """
        self.client_socket = socket.socket()
        self.client_socket.connect((self.server_ip, self.port))
        self._xchange_key()
        while self.is_socket_open and self.crypt_object is not None:
            try:
                len_of_message = int(self.client_socket.recv(self.zfill_number).decode())
            except Exception as e:
                print(e)
                sys.exit()
            try:
                encrypt_message = self.client_socket.recv(len_of_message).decode()
            except Exception as e:
                print(e)
                sys.exit()
            message = self.crypt_object.decrypt(encrypt_message)
            self.message_queue.put(message)

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
        message = clientProtocol.clientProtocol.build_part_of_key(B)
        len_of_message = str(len(message)).zfill(self.zfill_number)
        try:
            self.client_socket.send(f"{len_of_message}{message}".encode())
        except Exception as e:
            print(e)
        try:
            len_of_message = self.client_socket.recv(self.zfill_number).decode()
            message = self.client_socket.recv(int(len_of_message)).decode()
        except Exception as e:
            print(e)
        if message[:2] == "00":
            A = int(message[2:])
            crypt_object = Encryption_Decryption.AES_encryption.set_key(A, b)
            # exchange keys and create cryptObject
            self.crypt_object = crypt_object

    def send(self, message):
        """
        :param message:
        :return:
        """
        if self.crypt_object is not None and self.is_socket_open:
            encrypt_msg = self.crypt_object.encrypt(message)
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            try:
                self.client_socket.send(len_encrypt_msg + encrypt_msg)
            except Exception as e:
                print(e)

    def send_file(self, data, header):
        """

        :param data:
        :param header:
        :return:
        """
        if self.crypt_object is not None and self.is_socket_open:
            print(header, "header")
            encrypt_data = self.crypt_object.encrypt(data)
            len_encrypt_data = str(len(encrypt_data)).zfill(self.zfill_number).encode()
            print(len_encrypt_data, "lenedata")
            encrypt_header = self.crypt_object.encrypt(len_encrypt_data + header.encode())
            len_encrypt_header = str(len(encrypt_header)).zfill(self.zfill_number).encode()
            print(len_encrypt_header,"lene header")
            self.client_socket.send(len_encrypt_header + encrypt_header + encrypt_data)

    def close_socket(self):
        """
        :return:
        """
        self.is_socket_open = False


if __name__ == '__main__':
    q = queue.Queue()
    c = Clientcomm("192.168.1.129", q, 2000, 8)
    while c.crypt_object is None:
        continue
    file_name = "cat.jpg"
    with open(fr"F:\nexus\projectCode\files\{file_name}", 'rb') as f:
        data = f.read()

    header = clientProtocol.clientProtocol.Upload_file(file_name)
    c.send_file(data, header)
