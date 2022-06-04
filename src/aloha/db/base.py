from ..encrypt import vault
from ..logger import LOG
from ..settings import SETTINGS


class PasswordVault:
    _dict_cache_vault = {}

    @staticmethod
    def get_vault(vault_type: str = None, vault_config: dict = None, *args, **kwargs) -> vault.BaseVault:
        encryption_method = vault_type or SETTINGS.config.get('PASSWORD_ENCRYPTION')
        LOG.debug('Using password vault: %s', encryption_method)

        cache_key = '%s:%s' % (encryption_method, str(vault_config))
        if cache_key not in PasswordVault._dict_cache_vault:
            if encryption_method in ('plain', 'aes') or encryption_method is True:
                v = vault.AesVault(**(vault_config or {}))
            elif encryption_method == 'cyberark':
                config_cyberark = vault_config or SETTINGS.config.get('CYBERARK_CONFIG')
                if config_cyberark is None:
                    raise RuntimeError('Missing [CYBERARK_CONFIG] in config!')
                v = vault.CyberArkVault(**config_cyberark)
            else:
                LOG.info('Using plain password vault as unknown value of PASSWORD_ENCRYPTION=%s in config.', encryption_method)
                v = vault.DummyVault(**(vault_config or {}))
            PasswordVault._dict_cache_vault[cache_key] = v

        return PasswordVault._dict_cache_vault[cache_key]


def main():
    import sys
    config_key = sys.argv[-1]
    LOG.debug('Getting pwd for deploy key [deploy.%s]' % config_key)
    try:
        db_config = SETTINGS.config['deploy'][config_key]
        password_vault = PasswordVault.get_vault()
        p = password_vault.get_password(db_config.get('password'))
        LOG.debug("Decrypted PWD: %s" % p)
    except KeyError:
        LOG.error('Please make sure config key [deploy.%s] exists!' % config_key)
