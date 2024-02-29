class clientProtocol(object):
    @staticmethod
    def unpack(data):
        """
        :param data:
        :return:
        """
        params = data.split("$%$")
        opcode = params[0]
        params.remove(params[0])
        return opcode, params

    @staticmethod
    def unpack_file(data):
        """
        :param data:
        :return:
        """

        params = data.split("$%$")
        opcode = params[1]
        params.remove(params[1])
        return opcode, params

    @staticmethod
    def build_part_of_key(A):
        return f"00{A}"

    @staticmethod
    def request_torrent_file(file_name):
        """

        :param file_name:
        :return:
        """
        return f"01$%${file_name}"

    @staticmethod
    def request_upload(path):
        """

        :param path:
        :return:
        """
        return f"02$%${path}"

    @staticmethod
    def upload_file(filename):
        """

        :param filename:
        :return:
        """
        return f"$%$01$%${filename}"

    @staticmethod
    def request_part_file(file_name, number_of_part):
        return f"01$%${number_of_part}$%${file_name}"

    @staticmethod
    def send_file_part(file_name, number_of_part):
        return f"01$%${number_of_part}$%${file_name}$%$"

    @staticmethod
    def added_file_nitur(file_name):
        return f"01$%${file_name}"

    @staticmethod
    def removed_file_nitur(file_name):
        return f"02$%${file_name}"

    @staticmethod
    def changed_file_nitur(file_name):
        return f"03$%${file_name}"

    @staticmethod
    def changed_file_name_old_nitur(file_name):
        return f"04$%${file_name}"

    @staticmethod
    def changed_file_name_new_nitur(file_name):
        return f"05$%${file_name}"
