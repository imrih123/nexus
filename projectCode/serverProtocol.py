
class serverProtocol(object):
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
    def Response_for_torrent_request(json_torrent):
        return f"01$%${json_torrent}"

    @staticmethod
    def Response_for_upload_request(file_name, port):
        return f"02$%${port}$%${file_name}"

    @staticmethod
    def Response_for_upload():
        return "011"

    @staticmethod
    def Delete_file_from_folder(file_name):
        return f"03$%${file_name}"

    @staticmethod
    def Create_string_of_list(list_of_open_file):
        return f"03$%${'$%$'.join(list_of_open_file)}"
