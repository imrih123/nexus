
class serverProtocol(object):
    @staticmethod
    def unpack(data):
        """
        :param data: the data from the comm
        :return: opcode and params as list
        """
        params = data.split("$%$")
        opcode = params[0]
        params.remove(params[0])
        return opcode, params

    @staticmethod
    def unpack_file(data):
        """
        :param data:the data from the comm
        :return:opcode and params as list
        """
        params = data.split("$%$")
        opcode = params[1]
        params.remove(params[1])
        return opcode, params

    @staticmethod
    def build_part_of_key(A):
        """
        :param A: part of the key
        :return: a with format
        """
        return f"00{A}"

    @staticmethod
    def Response_for_torrent_request(file_name):
        """
        :param file_name: name of the file
        :return: response for the torrent request
        """
        return f"01$%$0$%${file_name}$%$"

    @staticmethod
    def Response_for_upload_request(path_of_file, port):
        """
        :param path_of_file: path
        :param port: port to use
        :return: path and port with format
        """
        return f"02$%${port}$%${path_of_file}"

    @staticmethod
    def Response_for_upload():
        return "111"

    @staticmethod
    def Delete_file_from_folder(file_name):
        """
        :param file_name: name of file to delete
        :return: the name with format
        """
        return f"03$%${file_name}"

    @staticmethod
    def Create_string_of_list(list_of_open_file):
        """
        :param list_of_open_file: list of all the open file
        :return: a sting in format with all the data on the files
        """
        message = "03"
        for file in list_of_open_file:
            if list_of_open_file[file][1] != 0:
                message += f"$%${file},{list_of_open_file[file][0]},{list_of_open_file[file][1]}"
        return message
