import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
import random
import chardet


class AES_encryption(object):
    def __init__(self, key):
        """

        :param key:
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(str(key).encode()).digest()

    def encrypt(self, message):
        """

        :param message:
        :return:
        """
        if type(message) == str:
            message = message.encode()
        raw = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, encrypt_message):
        """

        :param encrypt_message:
        :return:
        """
        enc = base64.b64decode(encrypt_message)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC,iv)
        a = self._unpad(cipher.decrypt(enc[AES.block_size:]))
        encoding = chardet.detect(a)
        if encoding['encoding'] == "ascii":
            a = a.decode()
        return a

    def _pad(self, message):
        """

        :param message:
        :return:
        """
        return message + (self.bs - len(message) % self.bs) * chr(self.bs - len(message) % self.bs).encode()

    def _unpad(self, message):
        """

        :param message:
        :return:
        """
        return message[:-ord(message[len(message) - 1:])]

    @staticmethod
    def hash(message):
        return hashlib.sha256(message).digest()

    @staticmethod
    def get_dif_Num():
        a = random.randint(1, p)
        return a, str((g**a) % p)

    @staticmethod
    def set_key(B, a):
        """

        :param A:
        :param B:
        :return:
        """
        return AES_encryption((int(B)**int(a)) % p)


p = 7723
g = 1229


if __name__ == '__main__':
    #server
    a,A = AES_encryption.get_dif_Num()
    # send
    # recv
    print(len(str(A)))

    # client
    b,B = AES_encryption.get_dif_Num()
    # recv
    # send

    keyServer = AES_encryption.set_key(B,a)
    keyclient = AES_encryption.set_key(A,b)
    print(keyclient.key)
    print(keyServer.key)



    with open (r"T:\public\יב\imri\projectCode\files\cat.jpg", 'rb') as f:
        data = f.read()
    data= "reef"
    #print(type(data))

    print(len(data))

    encM = keyServer.encrypt(data)
    print(len(encM), type(encM))

    decM = keyclient.decrypt(encM)
    print(decM)
    # data , path = decM[:8532], decM[8532:]
    # path.decode()
    # print(path)
    # print(len(decM))
    #with open(fr"T:\public\יב\imri\projectCode\files\cat22.jpg", 'wb') as f:
        #f.write(decM)
    #with open(r"temp.jpg", 'wb') as f:
        #f.write(decM)




    #print(msg, encM, decM)