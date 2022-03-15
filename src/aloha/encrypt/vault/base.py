from abc import ABC, abstractmethod
from urllib.parse import quote_plus as urlquote


class BaseVault(ABC):
    @abstractmethod
    def decrypt_password(self, *args, **kwargs):
        return kwargs.get('password')

    def get_password(self, *args, **kwargs):
        url_quote = kwargs.pop('url_quote', True)
        pwd = self.decrypt_password(*args, **kwargs)
        if url_quote:
            return urlquote(pwd)
        else:
            return pwd


class DummyVault(BaseVault):
    def decrypt_password(self, password):
        return password


def main():
    vault = DummyVault()
    ret = vault.get_password('1c3b988ed369d7c6126652aabb582b29', url_quote=True)
    # print(ret)
    return ret
