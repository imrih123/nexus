
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
    def build_part_of_key(A):
        return f"00{A}"

    @staticmethod
    def Request_torrent_file():
        return

    @staticmethod
    def Request_upload():
        return

    @staticmethod
    def Upload_file(filename):
        return f"$%$01$%${filename}"

    @staticmethod
    def Request_part_file():
        return

    @staticmethod
    def Send_file_part():
        return

    @staticmethod
    def Added_file_nitur():
        return

    @staticmethod
    def removed_file_nitur():
        return

    @staticmethod
    def changed_file_nitur():
        return