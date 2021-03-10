from .base import subparsers as parser
parser = parser['info']


def main():
    print('Aloha!')

    args, _ = parser.parse_known_args()
    if args.version:
        from .. import __version__
        print('Aloha version: %s' % __version__)
