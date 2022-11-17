import importlib
import os
import sys


def main():
    print('\n'.join(sorted('%s=%s' % (k, v) for k, v in os.environ.items())))

    usage = '''
    Usage: `python main.py app_common.main` ; or set environment variable `ENTRYPOINT` 
        the `module.name` should be a python package file or package which include a `main()` function
    '''

    try:
        module_name = sys.argv[1]
    except IndexError:
        module_name = os.environ.get('ENTRYPOINT')

    if module_name is None:
        print(usage)
        exit(-1)

    try:
        m = importlib.import_module(module_name)
    except ImportError:
        raise ValueError('Invalid entrypoint: %s' % module_name)

    f_main = getattr(m, 'main')

    if f_main is None:
        print('Given module does not provides a `main()` function!')
    else:
        print('Starting module: %s' % module_name)
        ret = f_main()
        if ret:
            print(ret)


if __name__ == '__main__':
    """aloha start module.name"""
    """python -m aloha.script.start module.name"""
    main()
