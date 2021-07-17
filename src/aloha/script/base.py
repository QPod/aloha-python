__all__ = ('parser', 'subparsers')

import argparse

_sub_commands = {
    'info': {
        'version': (('-v', '--version'), dict(action='count', default=0, help='display package version information'))
    },
    'compile': {
        'keep': (('-k', '--keep'), dict(action='append', default=[], help='source files keep as is and not converting to dynamic library')),
        'exclude': (('-x', '--exclude'), dict(action='append', default=[], help='list of files/folders to exclude')),
        'dist': (('-d', '--dist'), dict(default='build', help='target directory for build files')),
        'base': (('-b', '--base'), dict(default=None, help='base dir which will be traversed, use current directory by default'))
    }
}

parser = argparse.ArgumentParser()

_subparsers = parser.add_subparsers(dest='cmd', help="aloha sub-command")
subparsers = {}

for sub_command, args in _sub_commands.items():
    s = _subparsers.add_parser(sub_command)
    for a, (flags, params) in args.items():
        s.add_argument(*flags, **params)
    subparsers[sub_command] = s
