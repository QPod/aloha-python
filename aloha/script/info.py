from .base import subparsers as parser
parser = parser['info']


def main():
    print('Aloha!')

    args, _ = parser.parse_known_args()
    if args.version:
        print('123')
