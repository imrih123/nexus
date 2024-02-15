import Encryption_Decryption
import math
import json
import os
import settingSer

class Server_files(object):
    def __init__(self, torrent_files_path):
        self.torrent_files_path = torrent_files_path

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
        print("full hash ----", full_hash)
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
        with open(fr"{self.torrent_files_path}\\{file_name}.json", "r") as f:
            data = json.load(f)

        list_of_ip = data["open ip"]
        if ip not in list_of_ip:
            list_of_ip.append(ip)
        data["open ip"] = list_of_ip

        bol = len(data["open ip"]) == 1

        with open(fr"{self.torrent_files_path}\\{file_name}.json", "w") as f:
            json.dump(data, f)

        return bol

    def get_torrent_file(self, file_name):
        """

        :param file_name:
        :return:
        """
        data = None
        if os.path.exists(f"{self.torrent_files_path}\{file_name}.json"):
            with open(fr"{self.torrent_files_path}\\{file_name}.json", "r") as f:
                data = json.load(f)
                data = json.dumps(data)
        return data

    def delete_ip_from_torrent(self, file_name, ip):
        """

        :param file_name:
        :param ip:
        :return:
        """
        with open(fr"{self.torrent_files_path}\\{file_name}.json", "r") as f:
            data = json.load(f)

        list_of_ip = data["open ip"]
        if ip in list_of_ip:
            list_of_ip.remove(ip)
        data["open ip"] = list_of_ip

        bol = len(data["open ip"]) == 0

        with open(fr"{self.torrent_files_path}\\{file_name}.json", "w") as f:
            json.dump(data, f)
        return bol


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
