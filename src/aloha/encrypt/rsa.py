__all__ = ('RsaEncryptor',)

import base64
from functools import lru_cache
from typing import Tuple, Optional, Union

from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

t_cipher_module = Union[PKCS1_v1_5.PKCS115_Cipher, PKCS1_OAEP.PKCS1OAEP_Cipher]

_RSA_CIPHER_METHODS = {  # FULL_CIPHER_NAME: (module, dict_params)
    "RSA/ECB/PKCS1Padding": (PKCS1_v1_5, {'randfunc': None}),
    "RSA/ECB/OAEPWithSHA-1AndMGF1Padding": (PKCS1_OAEP, {'hashAlgo': SHA1, 'mgfunc': lambda x, y: pss.MGF1(x, y, SHA1)}),
    "RSA/ECB/OAEPWithSHA-256AndMGF1Padding": (PKCS1_OAEP, {'hashAlgo': SHA256, 'mgfunc': lambda x, y: pss.MGF1(x, y, SHA1)}),
}


class RsaEncryptor:
    _dict_cache_cipher = {}
    _dict_cache_decipher = {}
    supported_cipher_methods = _RSA_CIPHER_METHODS

    # ref: https://cryptobook.nakov.com/asymmetric-key-ciphers/rsa-encrypt-decrypt-examples
    def __init__(self, key_private: str = None, key_public: str = None, cipher_name: str = 'RSA/ECB/PKCS1Padding'):
        self.key_private, self.key_public = self.load_keys_from_string(key_private=key_private, key_public=key_public)
        assert self._get_cipher_module(cipher_name) is not None, 'Invalid cipher_name!'
        self.cipher_name = cipher_name

    @staticmethod
    def _get_cipher_module(full_cipher_name: str = None) -> Optional[Tuple]:
        try:
            return _RSA_CIPHER_METHODS[full_cipher_name]
        except KeyError:
            raise ValueError('Unsupported full cipher name, supported ones: %s.' % ','.join(sorted(_RSA_CIPHER_METHODS)))

    @staticmethod
    def generate_key_pair(size: int = 1024) -> Tuple[str, str]:
        key_pair = RSA.generate(size)
        key_private, key_public = key_pair.exportKey(), key_pair.publickey().exportKey()
        return key_private.decode('ascii'), key_public.decode('ascii')

    @lru_cache
    def get_cipher(self, key_public: str = None, cipher_name='RSA/ECB/PKCS1Padding') -> t_cipher_module:
        if key_public is None:
            key_pub = self.key_public
        else:
            _, key_pub = self.load_keys_from_string(key_public=key_public)
        if key_pub is None:
            raise RuntimeError('Public Key not set!')
        cache_key = key_pub.export_key(format='OpenSSH')
        if cache_key not in RsaEncryptor._dict_cache_cipher:
            pkcs_module, dict_param = self._get_cipher_module(cipher_name)
            RsaEncryptor._dict_cache_cipher[cache_key] = pkcs_module.new(key_pub, **dict_param)
        # debug: print('->PUB',  cache_key, len(RsaEncryptor._dict_cache_cipher))
        return RsaEncryptor._dict_cache_cipher[cache_key]

    @lru_cache
    def get_decipher(self, key_private: str = None, cipher_name='RSA/ECB/PKCS1Padding') -> t_cipher_module:
        if key_private is None:
            key_pri = self.key_private
        else:
            key_pri, _ = self.load_keys_from_string(key_private=key_private)
        if key_pri is None:
            raise RuntimeError('Private Key not set!')
        cache_key = key_pri.export_key(format='OpenSSH')
        if cache_key not in RsaEncryptor._dict_cache_decipher:
            pkcs_module, dict_param = self._get_cipher_module(cipher_name)
            RsaEncryptor._dict_cache_decipher[cache_key] = pkcs_module.new(key_pri, **dict_param)
        # debug: print('->PRI', cache_key, len(RsaEncryptor._dict_cache_decipher))
        return RsaEncryptor._dict_cache_decipher[cache_key]

    @staticmethod
    def load_keys_from_binary(key_private: bytes = None, key_public: bytes = None) -> Tuple[Optional[RSA.RsaKey], Optional[RSA.RsaKey]]:
        _key_private, _key_public = None, None

        if key_private is not None:
            try:
                _key_private = RSA.import_key(key_private)
            except ValueError as e:
                raise ValueError('RSA pri key format error: [%s]' % key_private)

        if key_public is not None:
            try:
                _key_public = RSA.import_key(key_public)
            except ValueError as e:
                raise ValueError('RSA pub key format error: [%s]' % key_public)

        return _key_private, _key_public

    @staticmethod
    def load_keys_from_string(key_private: str = None, key_public: str = None) -> Tuple[Optional[RSA.RsaKey], Optional[RSA.RsaKey]]:
        _key_private, _key_public = None, None

        if key_private is not None:
            if not key_private.startswith('-----'):
                key_pri = f'-----BEGIN RSA PRIVATE KEY-----\n{key_private}\n-----END RSA PRIVATE KEY-----'
            else:
                key_pri = key_private
            try:
                _key_private = RSA.import_key(key_pri)
            except ValueError as e:
                raise ValueError('RSA private key format error: [%s]' % key_pri)

        if key_public is not None:
            if not key_public.startswith('-----'):
                key_pub = f'-----BEGIN PUBLIC KEY-----\n{key_public}\n-----END PUBLIC KEY-----'
            else:
                key_pub = key_public
            try:
                _key_public = RSA.import_key(key_pub)
            except ValueError as e:
                raise ValueError('RSA public key format error: [%s]' % key_pub)

        return _key_private, _key_public

    def encrypt_with_public_key(self, message: Union[str, bytes], key_public: str = None, cipher_name: str = None) -> bytes:
        data = message if isinstance(message, bytes) else message.encode('UTF-8')
        cipher = self.get_cipher(key_public=key_public, cipher_name=cipher_name or self.cipher_name)
        return cipher.encrypt(data)

    def decrypt_with_private_key(self, ciphertext: Union[str, bytes], key_private: str = None, cipher_name: str = None, **kwargs) -> bytes:
        data = ciphertext if isinstance(ciphertext, bytes) else ciphertext.encode('ascii')
        decipher = self.get_decipher(key_private=key_private, cipher_name=cipher_name or self.cipher_name)
        return decipher.decrypt(data, **kwargs)

    @staticmethod
    def convert_bytes_to_base64(data: bytes) -> str:
        return base64.b64encode(data).decode()

    @staticmethod
    def convert_base64_to_bytes(data: str) -> bytes:
        return base64.decodebytes(data.encode('ascii'))


def main():
    key_pairs = [  # private_key, public_key
        RsaEncryptor.generate_key_pair(),
    ]

    for str_src in ('aloha!', '😄', '{"x": 1}'):
        for i, (key_pri, key_pub) in enumerate(key_pairs):
            rsa_enc = RsaEncryptor()
            x_enc = rsa_enc.encrypt_with_public_key(str_src, key_public=key_pub)
            x_txt = rsa_enc.convert_bytes_to_base64(x_enc)

            rsa_dec = RsaEncryptor()
            y_bin = rsa_dec.convert_base64_to_bytes(x_txt)
            y_dec = rsa_dec.decrypt_with_private_key(y_bin, key_private=key_pri)
            y_txt = y_dec.decode('UTF-8')

            print('[test {i_case} success = {status}] {src} -> {enc}'.format(
                i_case=i, status=(y_txt == str_src), src=y_txt, enc=x_txt
            ))
