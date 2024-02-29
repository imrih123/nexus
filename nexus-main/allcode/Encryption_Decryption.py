import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
import random


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
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

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

