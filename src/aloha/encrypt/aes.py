import base64
import binascii
from typing import Union, Callable, Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

_AES_CIPHER_METHODS = {  # FULL_CIPHER_NAME: (dict_params, pad_style)
    "AES/ECB/PKCS5Padding": ({'mode': AES.MODE_ECB}, 'pkcs7'),
    "AES/ECB/NoPadding": ({'mode': AES.MODE_ECB}, 'pkcs7'),
    "AES/CBC/PKCS7Padding": ({'mode': AES.MODE_CBC, 'iv': b'0000000000000000'}, 'pkcs7'),
    "AES/CBC/NoPadding": ({'mode': AES.MODE_CBC, 'iv': b'0000000000000000'}, 'x923'),
}


def _generate_key(key_size: int, method='const') -> bytes:
    if method == 'const':
        return b'0' * key_size  # b'b6046801716aec00'
    elif method == 'random':
        return get_random_bytes(key_size)
    raise ValueError('Invalid AES key generate method: [%s]' % method)


class AesEncryptor:
    supported_cipher_methods = _AES_CIPHER_METHODS

    def __init__(self, key: Union[str, bytes] = None, key_size: int = 16, cipher_name: str = 'AES/ECB/PKCS5Padding'):
        _key = key
        if key is None:
            _key = _generate_key(key_size)
        elif isinstance(key, str):
            _key = key.encode()

        if len(_key) not in (16, 24, 32,):
            raise ValueError("Invalid key size/length [%s] for AesEncryptor!" % len(_key))

        self.key_aes, self.block_size = _key, AES.block_size
        # https://pycryptodome.readthedocs.io/en/latest/src/util/util.html
        self.cipher_name = cipher_name

    def encrypt(self, text: str, output_format='hex', func_pad: Optional[Callable] = None) -> Union[str, bytes]:
        dict_params, pad_style = _AES_CIPHER_METHODS.get(self.cipher_name)
        if not callable(func_pad):
            func_pad = lambda x: pad(data, block_size=self.block_size, style=pad_style)

        data = text.encode()
        padded = func_pad(data)
        cipher = AES.new(key=self.key_aes, **dict_params)
        bytes_crypt = cipher.encrypt(padded)

        if output_format == 'hex':
            crypt = binascii.b2a_hex(bytes_crypt).decode()
        elif output_format == 'base64':
            crypt = base64.b64encode(bytes_crypt).decode()
        elif output_format in ('bytes', 'bin'):
            crypt = bytes_crypt
        else:
            raise ValueError('Unknown output_type [%s]' % output_format)
        return crypt

    def decrypt(self, text: Union[str, bytes], input_format: str = 'hex', func_unpad: Optional[Callable] = None) -> Union[str, bytes]:
        text += (len(text) % 4) * '='
        if input_format == 'hex':
            crypt = binascii.a2b_hex(text)
        elif input_format == 'base64':
            crypt = base64.b64decode(text)
        elif input_format in ('bytes', 'bin'):
            crypt = text
        else:
            raise ValueError('Unknown output_type [%s]' % input_format)
        dict_params, pad_style = _AES_CIPHER_METHODS.get(self.cipher_name)
        cipher = AES.new(key=self.key_aes, **dict_params)
        data = cipher.decrypt(crypt)
        if not callable(func_unpad):
            func_unpad = lambda x: unpad(x, block_size=self.block_size, style=pad_style)
        data = func_unpad(data)
        return data.decode('UTF-8')


def main():
    a = AesEncryptor()
    src = 'hello~'
    enc = a.encrypt(src, output_format='base64')
    dec = a.decrypt(enc, input_format='base64')
    # print(enc, dec, src == dec)
