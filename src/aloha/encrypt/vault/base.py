import abc

from urllib.parse import quote_plus as urlquote


class BaseVault(abc.ABC):
    @abc.abstractmethod
    def decrypt_password(self, *args, **kwargs):
        return kwargs.get('password')

    def get_password(self, password, *args, **kwargs):
        kwargs.update(password if isinstance(password, dict) else {'password': password})
        url_quote = kwargs.get('url_encode', True)

        pwd = self.decrypt_password(*args, **kwargs)
        if pwd is None:
            return None

        if url_quote:
            return urlquote(pwd)
        else:
            return pwd


class DummyVault(BaseVault):
    def decrypt_password(self, *args, **kwargs):
        return kwargs.get('password')


def main():
    vault = DummyVault()
    ret = vault.get_password(None, url_quote=True)
    # print(ret)
    return ret
