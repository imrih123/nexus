import socket
import select
import threading
import Encryption_Decryption
import queue
import time
import settingSer
import serverProtocol
import settingCli

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
        threading.Thread(target=self._recv_messages).start()

    def _recv_messages(self):
        """

        :return:
        """
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(3)
        while self.is_socket_open:
            rlist, wlist, xlist = select.select([self.server_socket] + list(self.open_clients.keys()),
                                                list(self.open_clients.keys()), [], 0.3)
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    (new_client, addr) = self.server_socket.accept()
                    threading.Thread(target=self._xchange_key, args=(new_client, addr)).start()
                else:
                    try:
                        len_of_message = int(current_socket.recv(self.zfill_number).decode())
                        encrypt_message = current_socket.recv(len_of_message)
                    except Exception as e:
                        print(e)
                        if self.port == settingSer.NITUR_PORT:
                            self.message_queue.put((self.open_clients[current_socket][0], "-1$%$"))
                        del self.open_clients[current_socket]
                    else:
                        message = self.open_clients[current_socket][1].decrypt(encrypt_message).decode()
                        if self.port in [settingSer.GENERAL_PORT, settingSer.NITUR_PORT, settingCli.P2P_PORT]:
                            self.message_queue.put((self.open_clients[current_socket][0], message))
                        else:
                            self._recv_file(current_socket, message)

    def _xchange_key(self, new_client, addr):
        """

        :return:
        """

        a, A = Encryption_Decryption.AES_encryption.get_dif_Num()
        try:
            len_of_message = new_client.recv(self.zfill_number).decode()
            message = new_client.recv(int(len_of_message)).decode()
        except Exception as e:
            print(e)
        else:
            B = int(message[2:])
            if message[:2] == "00":
                message = serverProtocol.serverProtocol.build_part_of_key(A)
                len_of_message = str(len(message)).zfill(self.zfill_number)
                try:
                    new_client.send(f"{len_of_message}{message}".encode())
                except Exception as e:
                    print(e)
                else:
                    cryptobject = Encryption_Decryption.AES_encryption.set_key(B, a)
                    # exchange keys and create cryptObject
                    self.open_clients[new_client] = [addr[0], cryptobject]
                    if self.port == settingSer.GENERAL_PORT:
                        self.message_queue.put((self.open_clients[new_client][0], "03"))

    def _find_socket_by_ip(self, find_ip):
        """

        :param find_ip:
        :return:
        """

        for key, value in self.open_clients.items():
            if value[0] == find_ip:
                return key

    def send(self, message, ip):
        """

        :param message:
        :param ip:
        :return:
        """
        current_socket = self._find_socket_by_ip(ip)
        if current_socket is not None and self.is_socket_open:
            encrypt_msg = self.open_clients[current_socket][1].encrypt(message.encode())
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            try:
                current_socket.send(len_encrypt_msg+encrypt_msg)
            except Exception as e:
                print(e)
                del self.open_clients[current_socket]

    def send_file(self, data, header, ip):
        """

        :param data:
        :param header:
        :return:
        """
        if self.is_socket_open:
            current_socket = self._find_socket_by_ip(ip)
            crypto = self.open_clients[current_socket][1]
            encrypt_data = crypto.encrypt(data)
            len_encrypt_data = str(len(encrypt_data)).zfill(self.zfill_number).encode()
            encrypt_header = crypto.encrypt(header.encode()+ len_encrypt_data)
            len_encrypt_header = str(len(encrypt_header)).zfill(self.zfill_number).encode()
            try:
                current_socket.send(len_encrypt_header + encrypt_header + encrypt_data)
            except Exception as e:
                print(e)
                del self.open_clients[current_socket]

    def sendall(self, message):
        """

        :param message:
        :return:
        """
        for sock in self.open_clients:
            try:
                ip = self.open_clients[sock][0]
                self.send(message, ip)
            except Exception as e:
                print(e)

    def _recv_file(self, current_socket, message):
        """

        :return:
        """
        opcode, params = serverProtocol.serverProtocol.unpack_file(message)
        len_encrypt_data = int(params[0])
        full_data = bytearray()
        while len_encrypt_data >= 1024:
            try:
                data = current_socket.recv(1024)
                full_data.extend(data)
            except Exception as e:
                print(e)
                del self.open_clients[current_socket]
            len_encrypt_data -= 1024
        if len_encrypt_data != 0:
            try:
                data = current_socket.recv(len_encrypt_data)
                full_data.extend(data)
            except Exception as e:
                print(e)
                del self.open_clients[current_socket]
        data = self.open_clients[current_socket][1].decrypt(full_data)
        params.append(data)
        params[0] = len(data)
        self.message_queue.put((self.open_clients[current_socket][0], params))

    def close_socket(self):
        """

        :return:
        """
        self.is_socket_open = False

