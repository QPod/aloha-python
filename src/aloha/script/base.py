import argparse
import importlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd')
    args, _ = parser.parse_known_args()

    cmd = args.cmd
    module = '%s.%s' % (__package__, cmd)
    try:
        module = importlib.import_module(module)
    except ImportError:
        print('Invalid sub-command: %s\n\tFailed to import: %s' % (cmd, module))
        exit(-1)

    func_main = getattr(module, 'main')

    exit(func_main())


if __name__ == '__main__':
    main()
