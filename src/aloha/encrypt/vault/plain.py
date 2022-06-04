import pyhocon

from .base import BaseVault
from ...encrypt.aes import AesEncryptor


def _is_empty_str(s):
    return s is None or isinstance(s, pyhocon.config_tree.NoneValue) or s == "None" or s == ""


class AesVault(AesEncryptor, BaseVault):
    def __init__(self, key: str = None):
        super().__init__(key)

    def decrypt_password(self, pwd):
        if _is_empty_str(pwd):
            return None
        return self.decrypt(pwd)


def main():
    vault = AesVault()
    pwd = vault.get_password(None, url_quote=True)
    # print(pwd)
    return pwd
