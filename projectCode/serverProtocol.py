
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
        print(params, "params")
        opcode = params[1]
        params.remove(params[1])
        return opcode, params

    @staticmethod
    def build_part_of_key(A):
        return f"00{A}"

    @staticmethod
    def Response_for_torrent_request():
        return

    @staticmethod
    def Response_for_upload_request():
        return

    @staticmethod
    def Response_for_upload ():
        return

    @staticmethod
    def Delete_file_from_folder():
        return

    @staticmethod
    def Create_string_of_list():
        return
