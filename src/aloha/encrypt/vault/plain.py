from .base import BaseVault
from ...encrypt.aes import AesEncryptor


class PlainVault(AesEncryptor, BaseVault):
    def __init__(self, key: str = None):
        super().__init__(key)

    def decrypt_password(self, password):
        return self.decrypt(password)


def main():
    vault = PlainVault()
    pwd = vault.get_password('1c3b988ed369d7c6126652aabb582b29', url_quote=True)
    # print(pwd)
    return pwd
