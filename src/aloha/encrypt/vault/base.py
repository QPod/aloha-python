from abc import ABC, abstractmethod
from urllib.parse import quote_plus as urlquote


class BaseVault(ABC):
    @abstractmethod
    def decrypt_password(self, *args, **kwargs):
        return kwargs.get('password')

    def get_password(self, *args, **kwargs):
        url_quote = kwargs.pop('url_quote', True)

        pwd = self.decrypt_password(*args, **kwargs)
        if pwd is None:
            return None

        if url_quote:
            return urlquote(pwd)
        else:
            return pwd


class DummyVault(BaseVault):
    def decrypt_password(self, password):
        return password


def main():
    vault = DummyVault()
    ret = vault.get_password(None, url_quote=True)
    # print(ret)
    return ret
