import importlib

from .base import parser, subparsers


def main():
    args, _ = parser.parse_known_args()

    cmd = args.cmd
    module = '%s.%s' % (__package__, cmd)
    try:
        module = importlib.import_module(module)
    except ImportError:
        print('Invalid sub-command: %s\n\tFailed to import: %s' % (cmd, module))
        exit(-1)

    func_main = getattr(module, 'main')

    sub_parser = subparsers[cmd]
    kwargs, _ = sub_parser.parse_known_args()
    kwargs = vars(kwargs)

    exit(func_main(**kwargs))


if __name__ == '__main__':
    main()
