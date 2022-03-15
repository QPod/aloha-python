import jwt

from ..logger import LOG

LOG.debug('Version of pyjwt = %s' % jwt.__version__.__str__())


def encode(
        secret_key: str,
        payload: dict,
        headers: dict = None,
        **kwargs
):
    token = jwt.encode(payload=payload, key=secret_key, headers=headers, **kwargs)
    return token


def decode(
        secret_key: str,
        token: str,
        **kwargs
):
    try:
        resp = jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'], **kwargs)
    except jwt.ExpiredSignatureError as e:
        resp = str(e)
    except jwt.PyJWTError as e:
        resp = str(e)
    return resp
