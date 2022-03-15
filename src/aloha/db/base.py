from ..logger import LOG
from ..settings import SETTINGS


def _get_vault():
    encryption_method = SETTINGS.config.get('PASSWORD_ENCRYPTION')
    LOG.info('Using password vault: %s', encryption_method)

    if encryption_method == 'plain' or encryption_method is True:
        from ..encrypt.vault.plain import PlainVault
        return PlainVault()
    elif encryption_method == 'cyberark':
        config_cyberark = SETTINGS.config.get('CYBERARK_CONFIG')
        if config_cyberark is None:
            LOG.error('Missing [CYBERARK_CONFIG] in config!')
            exit(-1)

        from ..encrypt.vault.cyberark import CyberArkVault
        return CyberArkVault(**config_cyberark)

    LOG.info('Using plain password vault as unknown value of PASSWORD_ENCRYPTION=%s in config.', encryption_method)

    from ..encrypt.vault.base import DummyVault
    return DummyVault()


password_vault = _get_vault()
