import os


class client_files(object):
    @staticmethod
    def add_part_of_file(path_of_file, number_of_part, data):
        with open(fr"{path_of_file}", 'wb') as f:
            f.seek(number_of_part * 4096)
            f.write(data)

    @staticmethod
    def get_part_of_file(path_of_file, number_of_part):
        with open(fr"{path_of_file}", 'rb') as f:
            if number_of_part == -1:
                data = f.read()
            else:
                f.seek(number_of_part * 4096)
                data = f.read(4096)
        return data

    @staticmethod
    def save_file(nitur_path, path_of_file, name_of_file):
        with open(fr"{path_of_file}", 'rb') as f:
            data = f.read()
        with open(fr"{nitur_path}\{name_of_file}", 'wb') as f:
            f.write(data)

    @staticmethod
    def delete_file(path_of_file, name_of_file):
        if os.path.exists(fr"{path_of_file}\\{name_of_file}"):
            os.remove(fr"{path_of_file}\\{name_of_file}")
