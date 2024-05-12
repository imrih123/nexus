class serverProtocol(object):
    @staticmethod
    def unpack(data):
        """
        :param data: the data from the comm
        :return:opcdoe and list of params
        """
        params = data.split("$%$")
        opcode = params[0]
        params.remove(params[0])
        return opcode, params

    @staticmethod
    def unpack_file(data):
        """
        :param data:the data of the comm
        :return: opcode and list of params
        """
        params = data.split("$%$")
        opcode = params[1]
        params.remove(params[1])
        return opcode, params

    @staticmethod
    def build_part_of_key(B):
        """

        :param B: part of the key
        :return: string using format
        """
        return f"00{B}"

    @staticmethod
    def Response_for_torrent_request(file_name):
        """

        :param file_name:the name of the file
        :return:string using format
        """
        return f"01$%$0$%${file_name}$%$"

    @staticmethod
    def Response_for_upload_request(path_of_file, port):
        """
        :param path_of_file: the path of the file
        :param port: the port
        :return: string using format
        """
        return f"02$%${port}$%${path_of_file}"

    @staticmethod
    def Response_for_upload(bol, path):
        """

        :param bol: fail or pass
        :return: string protocol
        """

        code = "222"
        if bol:
            code = "111"
        return f"04$%${code}$%${path}"

    @staticmethod
    def Delete_file_from_folder(file_name):
        """

        :param file_name: the file name
        :return: string using format
        """
        return f"03$%${file_name}"

    @staticmethod
    def Create_string_of_list(list_of_open_file):
        """

        :param list_of_open_file: list of all the open clients
        :return: string with the info of each file in the format
        """
        message = "03"
        for file in list_of_open_file:
            if list_of_open_file[file][1] != 0:
                message += f"$%${file},{list_of_open_file[file][0]},{list_of_open_file[file][1]}"
        return message
