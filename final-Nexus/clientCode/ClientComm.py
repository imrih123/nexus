import threading
import socket
from allcode import Encryption_Decryption
import sys
from clientCode import clientProtocol


class Clientcomm(object):
    def __init__(self, server_ip, message_queue, port, zfill_number, timer=1000):
        """
        :param server_ip: ip of the server
        :param message_queue: the queue to put the messages in for the logic
        :param port:the server port
        :param zfill_number: the number to zfill the message
        """
        self.server_ip = server_ip
        self.message_queue = message_queue
        self.port = port
        self.zfill_number = zfill_number
        self.client_socket = None
        self.crypt_object = None
        self.is_socket_open = True
        self.timer = timer
        threading.Thread(target=self._recv_messages).start()

    def _recv_messages(self):
        """
        the main loop the recv the messages
        """
        self.client_socket = socket.socket()
        try:
            self.client_socket.connect((self.server_ip, self.port))
        except Exception as e:
            print(e, f"cant connect to {self.server_ip}")
        else:
            self._xchange_key()
            while self.is_socket_open:
                try:
                    self.client_socket.settimeout(self.timer)
                    len_of_message = self.client_socket.recv(self.zfill_number).decode()
                except socket.timeout:
                    print("timeout", self.server_ip)
                    continue
                except Exception as e:
                    print(e)
                    sys.exit()
                if len_of_message == '':
                    self.close_socket()
                    break
                try:
                    self.client_socket.settimeout(self.timer)
                    encrypt_message = self.client_socket.recv(int(len_of_message)).decode()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(e)
                    sys.exit()
                message = self.crypt_object.decrypt(encrypt_message).decode()
                opcode, params = clientProtocol.clientProtocol.unpack(message)
                # if a header was recved
                if opcode == "01":
                    self._recv_file(params)
                else:
                    self.message_queue.put(message)

    def _recv_file(self, params):
        """
        :param params: list of params (the header)
        :return: put the data and the header of the file in the queue
        """
        number_of_part, file_name, data_len = int(params[0]), params[1], int(params[2])
        data_part = bytearray()
        while data_len >= 1024:
            try:
                self.client_socket.settimeout(self.timer)
                message = self.client_socket.recv(1024)
                data_part.extend(message)
            except socket.timeout:
                data_part = -1
                print("timeout")
                data_len = 0
                break
            except Exception as e:
                print(e)
                self.close_socket()
                sys.exit()
            else:
                data_len -= len(message)
        if data_len != 0:
            try:
                self.client_socket.settimeout(self.timer)
                data_part += self.client_socket.recv(data_len)
            except socket.timeout:
                data_part = -1
                print("timeout")
            except Exception as e:
                print(e)
                self.close_socket()
                sys.exit()
        data_part = self.crypt_object.decrypt(data_part)
        self.message_queue.put((self.server_ip, file_name, number_of_part, data_part))

    def _xchange_key(self):
        """
        create the AES object
        """
        b, B = Encryption_Decryption.AES_encryption.get_dif_Num()
        message = clientProtocol.clientProtocol.build_part_of_key(B)
        len_of_message = str(len(message)).zfill(self.zfill_number)
        try:
            self.client_socket.send(f"{len_of_message}{message}".encode())
        except Exception as e:
            print(e)
            sys.exit()
        try:
            len_of_message = self.client_socket.recv(self.zfill_number).decode()
            message = self.client_socket.recv(int(len_of_message)).decode()
        except Exception as e:
            print(e)
            sys.exit()
        if message[:2] == "00":
            A = int(message[2:])
            crypt_object = Encryption_Decryption.AES_encryption.set_key(A, b)
            # exchange keys and create cryptObject
            self.crypt_object = crypt_object

    def send(self, message):
        """
        :param message: the message to send
        send the message after encrypt to the server
        """
        while self.crypt_object is None:
            continue
        if self.crypt_object is not None and self.is_socket_open:
            encrypt_msg = self.crypt_object.encrypt(message)
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            try:
                self.client_socket.send(len_encrypt_msg + encrypt_msg)
            except Exception as e:
                print(e)

    def send_file(self, data, header):
        """
        send the file to the server
        :param data: the data of the file
        :param header: the header of the file
        """
        while self.crypt_object is None:
            continue
        if self.crypt_object is not None and self.is_socket_open:
            encrypt_data = self.crypt_object.encrypt(data)
            len_encrypt_data = str(len(encrypt_data)).zfill(self.zfill_number).encode()
            encrypt_header = self.crypt_object.encrypt(len_encrypt_data + header.encode())
            len_encrypt_header = str(len(encrypt_header)).zfill(self.zfill_number).encode()
            self.client_socket.send(len_encrypt_header + encrypt_header + encrypt_data)

    def close_socket(self):
        """
        close the socket and the main loop
        """
        self.is_socket_open = False
        self.client_socket.close()


