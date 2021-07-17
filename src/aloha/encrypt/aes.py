from binascii import b2a_hex, a2b_hex

import pyhocon
from Crypto.Cipher import AES


def _is_empty_str(s):
    return s is None or isinstance(s, pyhocon.config_tree.NoneValue) or s == "None" or s == ""


class AesEncryptor:
    def __init__(self, key: str = None):
        self.key = key or 'b6046801716aec00'

    def auto_fill_key(self):
        __key = self.key
        if len(__key) > 32:
            raise ValueError("Key length should be less than 32!")
        while len(__key) not in [16, 24, 32]:
            __key += " "
        return __key.encode()

    def encrypt(self, text):
        if _is_empty_str(text):
            return None

        text = text.encode('utf-8')
        cryptor = AES.new(self.auto_fill_key(), AES.MODE_CBC, b'0000000000000000')
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + (b'\0' * add)
        elif count > length:
            add = (length - (count % length))
            text = text + (b'\0' * add)
        ciphertext = cryptor.encrypt(text)
        return b2a_hex(ciphertext).decode()

    def decrypt(self, text):
        if _is_empty_str(text):
            return None

        cryptor = AES.new(self.auto_fill_key(), AES.MODE_CBC, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text.encode()))
        return plain_text.rstrip(b'\0').decode()
