import hashlib
from binascii import a2b_hex

import requests
from Crypto.Cipher import AES
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ..encrypt.aes import AesEncryptor
from ..logger import LOG

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class CyberarkVault(AesEncryptor):
    def __init__(self, url: str, app_id: str, key: str = None, safe: str = '', folder: str = 'root', env='DEV'):
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

    def decrypt(self, text):
        if text is None:
            return None

        cryptor = AES.new(self.auto_fill_key(), AES.MODE_ECB)
        s = cryptor.decrypt(a2b_hex(text.encode()))
        s = s[0: -s[-1]]
        return s.decode()

    def get_password(self, object=None, **kwargs):
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
                LOG.debug('POST Cyberark: %s with data: %s', self.url, data)
                resp = requests.post(self.url, json=data, verify=False, headers={'Content-Type': 'application/json'})
                tmp = resp.json()
                if resp.status_code == 200 and int(tmp['code']) == 200:
                    LOG.debug('Got data from Cyberark: %s', tmp)
                    return self.decrypt(tmp['password'])
                else:
                    raise RuntimeError(resp.text)
            except Exception as e:
                retry -= 1
                if retry == 0:
                    raise e
                else:
                    LOG.error('Cyberark request error: {}'.format(e))
        return None
