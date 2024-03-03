import os
from allcode import settingCli


class client_files(object):
    @staticmethod
    def add_part_of_file(path_of_file, number_of_part, data):
        """
        add the data to fhe file
        :param path_of_file: path of the file
        :param number_of_part: nunber of the part
        :param data: data of the file
        """
        with open(fr"{path_of_file}", 'wb') as f:
            f.seek(number_of_part * settingCli.BLOCKSIZE)
            f.write(data)

    @staticmethod
    def get_part_of_file(path_of_file, number_of_part):
        """

        :param path_of_file: path of the file
        :param number_of_part: number of the part
        :return: the data of the the part
        """
        with open(fr"{path_of_file}", 'rb') as f:
            if number_of_part == -1:
                data = f.read()
            else:
                f.seek(number_of_part * settingCli.BLOCKSIZE)
                data = f.read(settingCli.BLOCKSIZE)
        return data

    @staticmethod
    def save_file(nitur_path, name_of_file, data):
        """
        save the file
        :param nitur_path: the path to save
        :param name_of_file:the name of the file
        :param data:the data of the file
        :return:
        """
        with open(f"{nitur_path}\\{name_of_file}", 'wb') as f:
            f.write(data)

    @staticmethod
    def delete_file(path_of_file):
        """
        delete the file
        :param path_of_file:
        """
        if os.path.exists(fr"{path_of_file}"):
            os.remove(fr"{path_of_file}")

