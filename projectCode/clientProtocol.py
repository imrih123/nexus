
class clientProtocol(object):
    @staticmethod
    def unpack(data):
        """
        :param data:
        :return:
        """
        params = "$%$".split(data)
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
    def Request_torrent_file(file_name):
        """

        :param file_name:
        :return:
        """
        return f"01$%${file_name}"

    @staticmethod
    def Request_upload(path):
        """

        :param path:
        :return:
        """
        return f"02$%${path}"

    @staticmethod
    def Upload_file(filename):
        """

        :param filename:
        :return:
        """
        return f"$%$01$%${filename}"

    @staticmethod
    def Request_part_file(file_name, number_of_part):
        return f"01$%${number_of_part}$%${file_name}"

    @staticmethod
    def Send_file_part(file_name, number_of_part):
        return f"01$%${number_of_part}$%${file_name}"

    @staticmethod
    def Added_file_nitur(file_name):
        return f"01$%${file_name}"

    @staticmethod
    def removed_file_nitur(file_name):
        return f"02$%${file_name}"

    @staticmethod
    def changed_file_nitur(file_name):
        return f"03$%${file_name}"
