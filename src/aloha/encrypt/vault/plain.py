from .base import BaseVault
from ...encrypt.aes import AesEncryptor


class PlainVault(AesEncryptor, BaseVault):
    def __init__(self, key: str = None):
        super().__init__(key)

    def decrypt_password(self, password):
        return self.decrypt(password)


def main():
    vault = PlainVault()
    pwd = vault.get_password(None, url_quote=True)
    # print(pwd)
    return pwd
