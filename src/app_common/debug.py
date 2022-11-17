def main():
    from aloha.service.app import Application
    from aloha.settings import SETTINGS
    modules_to_load = [
        'app_common.api.api_common_sys_info'
    ]

    if 'service' not in SETTINGS.config:
        SETTINGS.config['service'] = {}

    SETTINGS.config['service'].update({
        'modules': modules_to_load,
        'debug': True,
    })

    # load the service modules from SETTINGS.config['service']['modules']
    app = Application()
    app.start()


if __name__ == '__main__':
    main()
