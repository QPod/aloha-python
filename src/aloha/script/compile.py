#!/usr/bin/env python3
# This script build a given python package into a package of dynamic library (.so) files.

__all__ = ('build', 'package')

import argparse
import glob
import os
import shutil
import time
from collections import defaultdict
from distutils.core import setup

try:
    from Cython.Build import cythonize
except ImportError:
    raise RuntimeError('Please pip install Cython first!')


def _expand(patterns: list = None):
    files = []
    for pattern in patterns:
        for file in glob.glob(pattern):
            files.append(os.path.abspath(file))
    files = sorted(set(files))
    return files


def _delete(file_path: str, ignore_errors=True):
    print('Removing file/folder: %s' % file_path)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        if not ignore_errors:
            raise e


def build(base: str = None, dist: str = 'build', exclude: list = None, keep: list = None, copy_others=True):
    path_base = os.path.abspath(base)
    path_build = os.path.abspath(dist)
    files_exclude = _expand(exclude or [])  # sorted(set(os.path.abspath(i) for i in files_exclude))
    files_keep = _expand(keep or [])  # sorted(set((os.path.abspath(i) for i in files_keep)))

    # decide which files to copy and which files to cythonize
    act_list = defaultdict(list)
    for dir_path, dir_names, file_names in os.walk(path_base):
        dir_name = dir_path.split(os.sep)[-1]  # name of the current directory

        if dir_path.startswith(path_build) or dir_path in files_exclude:
            continue  # skip: folder for build output, and excluded folders

        if dir_name.startswith('.') or (os.sep + '.' in dir_path):
            continue  # hidden folders and sub-folders

        for file in file_names:
            (name, extension), path = os.path.splitext(file), os.path.join(dir_path, file)

            if path in files_exclude or extension in ('.pyc', 'pyx') or name.startswith('.'):
                continue  # skip: excluded files, pyc/pyx files, and hidden files

            path_full = os.path.abspath(path)

            action = 'copy'
            if extension in ('.py',):
                if not name.startswith('__') and path_full not in files_keep:
                    action = 'cythonize'
            elif not copy_others:
                continue  # if not copying other files, skip the file

            dst = path.replace(path_base, path_build)

            act_list[action].append((path, dst))

    for (src, dst) in act_list.get('copy', ()) + act_list.get('cythonize', ()):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)

    target_cythonize = [dst for (src, dst) in act_list.get('cythonize', ())]

    n_parallel = os.cpu_count() or 8

    # python code -> c code
    cythonized = cythonize(target_cythonize, nthreads=n_parallel, language_level=3)

    # c code -> dynamic library file
    path_build_tmp = os.path.join(path_build, '.tmp')
    script_args = ["build_ext", "-b", path_build, "-t", path_build_tmp, "-j", n_parallel]
    print('Build args: %s' % ' '.join(str(s) for s in script_args))
    setup(ext_modules=cythonized, script_args=script_args)

    # clean up
    for c_module in cythonized:
        for c_file in c_module.sources:
            _delete(c_file)
    for py_file in target_cythonize:
        _delete(py_file)
    _delete(path_build_tmp)


def package(base: str = None, dist: str = 'build', exclude: list = None, keep: list = None, copy_others=True, *args, **kwargs):
    t = time.time()

    path_base = os.path.abspath(base or './')
    path_dist = os.path.abspath(dist)
    os.makedirs(path_dist, exist_ok=True)
    if len(glob.glob(path_dist + '/*')) > 0:
        raise ValueError('Dist folder [%s] MUST be an empty directory or an non-existing folder!' % path_dist)

    folder_name = os.getcwd().split(os.sep)[-1]
    folder_temp = os.path.join('/tmp/build/', folder_name)
    print('Building project to path:', folder_temp)
    _delete(folder_temp, ignore_errors=True)  # clear the folder first

    build(
        base=path_base,  # use current directory by default
        dist=folder_temp,  # target directory for build files
        exclude=exclude,  # exclude this file by default, this is a collection of files/folders to exclude
        keep=keep,  # source files keep as is and not converting to dynamic library
        copy_others=copy_others
    )
    [shutil.move(f, os.path.join(path_dist, f.split(os.sep)[-1])) for f in glob.glob(folder_temp + '/*')]
    t = time.time() - t
    print('\n\nTime consumed to build code: %.2f seconds.' % t)
    print("Successfully finished building package to: ", path_dist)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=str, help='root folder which includes source code to build')
    p.add_argument('--dist', type=str, default='build', help='target folder for the binary code')
    p.add_argument('--exclude', type=str, nargs='*', default=(), help='a collection of files/folders to exclude')
    p.add_argument('--keep', type=str, nargs='*', default=(), help='source files keep as is and not converting to dynamic library')

    args = p.parse_args()
    args = vars(args)
    for k, v in args.items():
        print('%s = %s' % (k, v))
    package(**args)


if __name__ == '__main__':
    """python -m aloha.script.compile --base=./ --dist=../build --keep='main.py'"""
    main()
