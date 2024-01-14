import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
import random


class encryption_decryption(object):
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
        return self._unpad(
            cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, message):
        """

        :param message:
        :return:
        """
        print(type(message))
        print(type((self.bs - len(message) % self.bs)))
        print(type(chr(self.bs - len(message) % self.bs)))
        return message + (self.bs - len(message) % self.bs) * chr(self.bs - len(message) % self.bs).encode()

    def _unpad(self, message):
        """

        :param message:
        :return:
        """
        return message[:-ord(message[len(message) - 1:])]


def hash(message):
    return

def get_dif_Num():
    a = random.randint(1, p)
    return (a, (g**a) % p)


def set_key(B, a):
    """

    :param A:
    :param B:
    :return:
    """
    return encryption_decryption((B**a)%p)


p = 7723
g = 1229


if __name__ == '__main__':
    #server
    a,A = get_dif_Num()
    # send
    # recv


    # client
    b,B = get_dif_Num()
    # recv
    # send

    keyServer = set_key(B,a)
    keyclient = set_key(A,b)



    with open (r"T:\public\יב\imri\projectCode\files\cat.jpg", 'rb') as f:
        data = f.read()
    encM = keyServer.encrypt(data)
    decM = keyclient.decrypt(encM).encode()

    # with open(r"temp.jpg", 'wb') as f:
    #     f.write(decM.encode())


    print(type(encM))

    #print(msg, encM, decM)