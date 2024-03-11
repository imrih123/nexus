class clientProtocol(object):
    @staticmethod
    def unpack(data):
        """
        :param data: the data from the comm
        :return: opcode and list of params
        """
        params = data.split("$%$")
        opcode = params[0]
        params.remove(params[0])
        return opcode, params

    @staticmethod
    def unpack_file(data):
        """
        :param data: the data from the comm
        :return: the opcode and params
        """

        params = data.split("$%$")
        opcode = params[1]
        params.remove(params[1])
        return opcode, params

    @staticmethod
    def build_part_of_key(A):
        """
        :param A: part of the key
        :return: the format
        """
        return f"00{A}"

    @staticmethod
    def request_torrent_file(file_name):
        """

        :param file_name: the file name
        :return: string using the format
        """
        return f"01$%${file_name}"

    @staticmethod
    def request_upload(path):
        """

        :param path:path of the file
        :return:sting using the format
        """
        return f"02$%${path}"

    @staticmethod
    def upload_file(filename):
        """

        :param filename: the fuile name
        :return: sting using the format
        """
        return f"$%$01$%${filename}"

    @staticmethod
    def request_part_file(file_name, number_of_part, len_of_part):
        """
        :param file_name: the file name
        :param number_of_part: the number of the part
        :param len_of_part: the len of each part
        :return: string using the format
        """
        return f"01$%${number_of_part}$%${file_name}$%${len_of_part}"

    @staticmethod
    def send_file_part(file_name, number_of_part):
        """
        :param file_name: the file name
        :param number_of_part: the number of the part
        :return: string using format
        """
        return f"01$%${number_of_part}$%${file_name}$%$"

    @staticmethod
    def added_file_nitur(file_name):
        """
        :param file_name: file name
        :return: string using format
        """
        return f"01$%${file_name}"

    @staticmethod
    def removed_file_nitur(file_name):
        """
        :param file_name: file name
        :return: string using format
        """
        return f"02$%${file_name}"

    @staticmethod
    def changed_file_nitur(file_name):
        """
        :param file_name: file name
        :return: string using format
        """
        return f"03$%${file_name}"

    @staticmethod
    def changed_file_name_old_nitur(file_name):
        """
        :param file_name: file name
        :return: sting using format
        """
        return f"04$%${file_name}"

    @staticmethod
    def changed_file_name_new_nitur(file_name):
        """
        :param file_name: file name
        :return: sting using format
        """
        return f"05$%${file_name}"
