import os
from allcode import settingCli


class client_files(object):
    @staticmethod
    def add_part_of_file(path_of_file, number_of_part, data):
        """

        :param path_of_file:
        :param number_of_part:
        :param data:
        :return:
        """
        with open(fr"{path_of_file}", 'wb') as f:
            f.seek(number_of_part * settingCli.BLOCKSIZE)
            f.write(data)

    @staticmethod
    def get_part_of_file(path_of_file, number_of_part):
        """

        :param path_of_file:
        :param number_of_part:
        :return:
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
        :param nitur_path:
        :param name_of_file:
        :param data:
        :return:
        """
        with open(f"{nitur_path}\\{name_of_file}", 'wb') as f:
            f.write(data)

    @staticmethod
    def delete_file(path_of_file):
        """
        :param path_of_file:
        :return:
        """
        if os.path.exists(fr"{path_of_file}"):
            os.remove(fr"{path_of_file}")

