from aloha.service.app import Application
from aloha.settings import SETTINGS


def main():
    SETTINGS.config['service'] = {
        'modules': [
            'app_demo.common.api_sys_info'
        ],
        'debug': True
    }

    app = Application()
    app.start()


if __name__ == '__main__':
    main()
