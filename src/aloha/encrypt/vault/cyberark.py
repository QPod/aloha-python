import hashlib
import requests
from Crypto.Cipher import AES
from binascii import a2b_hex
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .base import BaseVault
from ...encrypt.aes import AesEncryptor
from ...logger import LOG

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGHT:!DH:!aNULL'


class CyberArkVault(BaseVault, AesEncryptor):
    _cached: dict = {}

    def __init__(self, url: str, app_id: str, key: str = None, safe: str = 'AIM_ELIS_LAS', folder: str = 'root'):
        super().__init__(key)
        self.url = url
        self.app_id = app_id
        self.safe = safe
        self.folder = folder

    @staticmethod
    def get_sign(appid, keyvalue):
        hash_string = appid + "&" + keyvalue
        sha256 = hashlib.sha256()
        sha256.update(hash_string.encode("utf8"))
        return sha256.hexdigest()

    def decrypt_password(self, text):
        if text is None:
            return None

        cryptor = AES.new(self.auto_fill_key(), AES.MODE_ECB)
        s = cryptor.decrypt(a2b_hex(text.encode()))
        s = s[0: -s[-1]]
        return s.decode()

    def get_cyberark_password(self, object=None, **kwargs):
        if isinstance(object, dict):
            kwargs.update(object)
        elif isinstance(object, str):
            kwargs.update({'object': object})

        app_id = kwargs.get('app_id', self.app_id)
        data = {
            "appId": app_id,
            "safe": kwargs.get('safe', self.safe),
            "folder": kwargs.get('folder', self.folder),
            "object": kwargs.get('object', object),
            "sign": self.get_sign(app_id, self.key)
        }

        retry = 5
        while retry:
            try:
                LOG.debug('POST CyberArk: %s with data: %s', self.url, data)
                resp = requests.post(self.url, json=data, verify=False, headers={'Content-Type': 'application/json'})
                tmp = resp.json()
                if resp.status_code == 200 and int(tmp['code']) == 200:
                    LOG.debug('Got data from CyberArk: %s', tmp)
                    return self.decrypt_password(tmp['password'])
                else:
                    raise RuntimeError(resp.text)
            except Exception as e:
                retry -= 1
                if retry == 0:
                    raise e
                else:
                    LOG.error('CyberArk request error: {}'.format(e))
        return None

    def get_password(self, object=None, **kwargs):
        key_for_cache = '{app_id};{safe};{folder};{key};{object}'.format(
            app_id=self.app_id, safe=self.safe, folder=self.folder, key=self.key, object=object
        )
        if key_for_cache not in self._cached:
            pwd = self.get_cyberark_password(object=object, **kwargs)
            self._cached[key_for_cache] = pwd
        else:
            LOG.debug('Using cached CyberArk key: %s' % key_for_cache)

        return self._cached[key_for_cache]


def main():
    vault = CyberArkVault(
        url='https://localhost/pidms/rest/pwd/getPassword',
        app_id='',
        safe='',
        folder='root',
        key='',
    )

    for _ in range(5):
        pwd = vault.get_password({'object': 'DB-*'})
        # print(pwd)
