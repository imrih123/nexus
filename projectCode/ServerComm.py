import socket
import select
import threading
import Encryption_Decryption
import sys
import queue
import time
import setting
import serverProtocol


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
                    # self._xchange_key()
                    threading.Thread(target=self._xchange_key, args=(new_client, addr)).start()
                else:
                    try:
                        len_of_message = int(current_socket.recv(self.zfill_number).decode())
                        encrypt_message = current_socket.recv(len_of_message)
                    except Exception as e:
                        print(e)
                        sys.exit()
                    message = self.open_clients[current_socket][1].decrypt(encrypt_message)
                    if self.port in [setting.GENERAL_PORT, setting.NITUR_PORT]:
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
        if current_socket is not None:
            encrypt_msg = self.open_clients[current_socket][1].encrypt(message.encode())
            len_encrypt_msg = str(len(encrypt_msg)).zfill(self.zfill_number).encode()
            current_socket.send(len_encrypt_msg+encrypt_msg)

    def sendall(self, message):
        """

        :param message:
        :return:
        """
        for ip in self.open_clients.keys():
            self.send(message, ip)

    def _recv_file(self, current_socket, message):
        """

        :return:
        """
        opcode, params = serverProtocol.serverProtocol.unpack_file(message)
        len_encrypt_data = int(params[0])
        data = bytearray()
        while len_encrypt_data >= 1024:
            try:
                data.extend(current_socket.recv(1024))
            except Exception as e:
                print(e)
            len_encrypt_data -= 1024
        if len_encrypt_data != 0:
            try:
                data.extend(current_socket.recv(len_encrypt_data))
            except Exception as e:
                print(e)
        data = self.open_clients[current_socket][1].decrypt(data)
        params.append(data)
        params[0] = len(data)
        self.message_queue.put((self.open_clients[current_socket][0], params))

    def close_socket(self):
        """

        :return:
        """
        self.is_socket_open = False


if __name__ == '__main__':
    q = queue.Queue()
    s = ServerComm(2000, q, 8)
    path_to_save = fr"T:\public\יב\imri\nexus\projectCode\files"
    while True:
        ip, params = q.get()
        print(params)
        print(f"the ip that send the file is {ip}")
        print(f"the file len is {params[0]}")
        print(f"the file name is {params[1]}")
        with open(fr"{path_to_save}\catS.jpg", 'wb') as f:
            f.write(params[2])