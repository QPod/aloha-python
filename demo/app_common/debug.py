def main():
    from aloha.service import DefaultHandler404
    from aloha.service.app import Application
    from aloha.settings import SETTINGS

    modules_to_load = [
        "app_common.api.api_common_sys_info",
        "app_common.api.api_common_query_postgres",
        "app_common.api.api_multipart",
    ]

    if 'service' not in SETTINGS.config:
        SETTINGS.config['service'] = {}

    # load the service modules from SETTINGS.config['service']['modules']
    SETTINGS.config['service'].update({
        'modules': modules_to_load,
        'debug': True,
    })

    # Use self defined 404 handler
    SETTINGS.config['default_handler_class'] = DefaultHandler404

    app = Application()

    # The event loop starts after start.
    app.start()


if __name__ == '__main__':
    main()
