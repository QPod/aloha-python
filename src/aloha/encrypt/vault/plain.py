from ..encrypt.aes import AesEncryptor


class PlainVault(AesEncryptor):
    def __init__(self, key: str = None):
        super().__init__(key)

    def get_password(self, object):
        return self.decrypt(object)
