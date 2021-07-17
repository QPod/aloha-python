def main(**kwargs):
    print('Aloha!')

    if kwargs.get('version'):
        from .. import __version__
        print('Aloha version: %s' % __version__)
