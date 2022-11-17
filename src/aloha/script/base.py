import sys
import argparse
import importlib


def main():
    if '' not in sys.path:  # if start from script, cwd is not include in sys.path
        sys.path.insert(0, '')

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd')
    args, _ = parser.parse_known_args()

    cmd = args.cmd
    module = '%s.%s' % (__package__, cmd)
    try:
        module = importlib.import_module(module)
    except ImportError as e:
        print('Invalid sub-command: %s\n\tFailed to import: %s' % (cmd, module))
        print(str(e))
        exit(-1)

    sys.argv.pop(0)
    print('aloha command options: %s' % ''.join(sys.argv))
    func_main = getattr(module, 'main')

    exit(func_main())


if __name__ == '__main__':
    main()
