from allcode import Encryption_Decryption
import math
import json
import os
import ctypes


class Server_files(object):
    def __init__(self, torrent_files_path):
        """
        :param torrent_files_path: the path of the torrent
        """
        self.torrent_files_path = torrent_files_path
        # create the dir
        if not os.path.exists(torrent_files_path):
            os.mkdir(torrent_files_path)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(torrent_files_path)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(torrent_files_path, attrs | 2)

    def create_torrent_file(self, data, filename):
        """
        create the torrent file
        :param data: the data of the file
        :param filename: the name of the file
        """
        list_of_hash = []
        # do-to calculate the len of each part
        len_of_part = 0
        len_of_part = max(4096, len_of_part)
        for i in range(math.ceil(len(data)/len_of_part)):
            data_part = data[i*len_of_part:(i+1)*len_of_part]
            list_of_hash.append(str(Encryption_Decryption.AES_encryption.hash(data_part)))
        full_hash = str(Encryption_Decryption.AES_encryption.hash(data))
        torrent_file = self._build_torrent_file\
            (data, filename, full_hash, list_of_hash, len_of_part)
        with open(f"{self.torrent_files_path}\\{filename}.json", 'w') as f:
            json.dump(torrent_file, f)

    def _build_torrent_file(self, file_data, file_name, full_hash, parts_hash, len_of_part):
        """

        :param file_data: the data
        :param file_name: the name
        :param full_hash: the full hash of the file
        :param parts_hash: list of the parts hash
        :return:
        """
        json_file = {"file name": file_name, "open ip": [],
                     "len of file": len(file_data), "number of pieces": len(parts_hash),
                     "hash of pieces": parts_hash, "full hash": full_hash, "part len": len_of_part}
        return json_file

    def add_ip_to_torrent(self, file_name, ip):
        """
        add ip to the list of open ips
        :param file_name: the name
        :param ip: the ip
        """
        with open(f"{self.torrent_files_path}\\{file_name}.json", "r") as f:
            data = json.load(f)

        list_of_ip = data["open ip"]
        if ip not in list_of_ip:
            list_of_ip.append(ip)
        data["open ip"] = list_of_ip

        with open(f"{self.torrent_files_path}\\{file_name}.json", "w") as f:
            json.dump(data, f)
        return

    def get_torrent_file(self, file_name, string=True):
        """

        :param file_name: the name
        :param string: return as a string
        :return: the torrent
        """
        data = None
        if os.path.exists(f"{self.torrent_files_path}\\{file_name}.json"):
            with open(f"{self.torrent_files_path}\\{file_name}.json", "r") as f:
                data = json.load(f)
                if string:
                    data = json.dumps(data)
        return data

    def delete_ip_from_torrent(self, file_name, ip):
        """
        remove the ip from the open ip list
        :param file_name: the name of the file
        :param ip: the ip
        """
        boolean = False
        with open(f"{self.torrent_files_path}\\{file_name}.json", "r") as f:
            data = json.load(f)

        list_of_ip = data["open ip"]
        if ip in list_of_ip:
            list_of_ip.remove(ip)
            boolean = True
        data["open ip"] = list_of_ip

        with open(f"{self.torrent_files_path}\\{file_name}.json", "w") as f:
            json.dump(data, f)
        return boolean

    def handdle_disconnect(self, ip):
        """
        remove the ip of every torrent file
        :param ip: the ip of the client
        :return: list of the file that have been deleted
        """
        list_of_deleted_ips = []
        files_name = os.listdir(self.torrent_files_path)
        for name in files_name:
            boolean = self.delete_ip_from_torrent(name[:-5], ip)
            if boolean:
                list_of_deleted_ips.append(name[:-5])

        return list_of_deleted_ips

