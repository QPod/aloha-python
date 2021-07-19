from ..logger import LOG
from ..settings import SETTINGS


def _get_vault():
    password_encryption = SETTINGS.config.get('PASSWORD_ENCRYPTION')
    LOG.info('Using password vault: %s', password_encryption)

    if password_encryption == 'plain' or password_encryption is True:
        from ..encrypt.vault.plain import PlainVault
        return PlainVault()
    elif password_encryption == 'cyberark':
        config_cyberark = SETTINGS.config.get('CYBERARK_CONFIG')
        if config_cyberark is None:
            LOG.error('Missing [CYBERARK_CONFIG] in config!')
            exit(-1)

        from ..encrypt.vault.cyberark import CyberarkVault
        return CyberarkVault(**config_cyberark)

    LOG.info('Using plain password vault as unknown value of PASSWORD_ENCRYPTION=%s in config.', password_encryption)

    from ..encrypt.vault.dummy import DummyVault
    return DummyVault()


password_vault = _get_vault()
