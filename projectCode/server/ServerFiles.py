import Encryption_Decryption
import math
import json
import os
import settingSer
import ctypes


class Server_files(object):
    def __init__(self, torrent_files_path):
        self.torrent_files_path = torrent_files_path
        if not os.path.exists(torrent_files_path):
            os.mkdir(torrent_files_path)
            attrs = ctypes.windll.kernel32.GetFileAttributesW(torrent_files_path)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(torrent_files_path, attrs | 2)

    def create_torrent_file(self, data, filename):
        """

        :param data:
        :param filename:
        :return:
        """
        list_of_hash = []
        for i in range(math.ceil(len(data)/settingSer.BLOCKSIZE)):
            data_part = data[i*settingSer.BLOCKSIZE:(i+1)*settingSer.BLOCKSIZE]
            list_of_hash.append(str(Encryption_Decryption.AES_encryption.hash(data_part)))
        full_hash = str(Encryption_Decryption.AES_encryption.hash(data))
        torrent_file = self._build_torrent_file\
            (data, filename, full_hash, list_of_hash)
        with open(f"{self.torrent_files_path}\\{filename}.json", 'w') as f:
            json.dump(torrent_file, f)

    def _build_torrent_file(self, file_data, file_name, full_hash, parts_hash):
        """

        :param file_data:
        :param file_name:
        :param full_hash:
        :param parts_hash:
        :return:
        """
        json_file = {"file name": file_name, "open ip": [],
                     "len of file": len(file_data), "number of pieces": len(parts_hash),
                     "hash of pieces": parts_hash, "full hash": full_hash}
        return json_file

    def add_ip_to_torrent(self, file_name, ip):
        """

        :param file_name:
        :param ip:
        :return:
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

    def get_torrent_file(self, file_name):
        """

        :param file_name:
        :return:
        """
        data = None
        if os.path.exists(f"{self.torrent_files_path}\\{file_name}.json"):
            with open(f"{self.torrent_files_path}\\{file_name}.json", "r") as f:
                data = json.load(f)
                data = json.dumps(data)
        return data

    def delete_ip_from_torrent(self, file_name, ip):
        """

        :param file_name:
        :param ip:
        :return:
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

        :param ip:
        :return:
        """
        list_of_deleted_ips = []
        files_name = os.listdir(self.torrent_files_path)
        for name in files_name:
            boolean = self.delete_ip_from_torrent(name[:-5], ip)
            if boolean:
                list_of_deleted_ips.append(name[:-5])

        return list_of_deleted_ips


if __name__ == '__main__':
    s = Server_files(fr"T:\public\יב\imri\nexus\projectCode\\torrent_files")
    with open(fr"T:\public\יב\imri\nexus\projectCode\torrent_files\cat.jpg.json", "rb") as f:
        data = f.read()
    s.create_torrent_file(data, "imri.jpg")
    print(s.add_ip_to_torrent("cat.jpg","127"))
    print(s.add_ip_to_torrent("cat.jpg", "127"))
    print(s.delete_ip_from_torrent("cat.jpg", "127"))
    print(s.delete_ip_from_torrent("cat.jpg", "128"))
    data = s.get_torrent_file("cat.jpg")
    print(data["open ip"])
