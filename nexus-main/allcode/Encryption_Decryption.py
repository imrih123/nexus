import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
import random


class AES_encryption(object):
    def __init__(self, key):
        """

        :param key: the key
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(str(key).encode()).digest()

    def encrypt(self, message):
        """

        :param message: the message to encrypt
        :return: the encrypted message
        """
        if type(message) == str:
            message = message.encode()
        raw = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, encrypt_message):
        """

        :param encrypt_message: the message after encrypt
        :return: the origin message
        """
        enc = base64.b64decode(encrypt_message)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, message):
        """

        :param message: the message
        :return: message with pading
        """
        return message + (self.bs - len(message) % self.bs) * chr(self.bs - len(message) % self.bs).encode()

    def _unpad(self, message):
        """

        :param message: the message with pad
        :return: the message
        """
        return message[:-ord(message[len(message) - 1:])]

    @staticmethod
    def hash(message):
        """

        :param message: the message
        :return: the message after hash
        """
        return hashlib.sha256(message).digest()

    @staticmethod
    def get_dif_Num():
        """
        :return: 2 numbers in dif format
        """
        a = random.randint(1, p)
        return a, str((g**a) % p)

    @staticmethod
    def set_key(B, a):
        """

        :param A:
        :param B:
        :return: the key
        """
        return AES_encryption((int(B)**int(a)) % p)


p = 7723
g = 1229

