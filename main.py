#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import os
import sys
from glob import glob
from pathlib import Path

try:
    from importlib.metadata import PackageNotFoundError, version

    manual_version_lookup = False
except ModuleNotFoundError:
    manual_version_lookup = True

from stdlib_list import stdlib_list


def main(proj_directory):
    py_files = glob(f'{Path(proj_directory).expanduser()}/**/*.py',
                    recursive=True)
    local_modules = [str(Path(x).stem) for x in py_files]
    files = [x for x in py_files if x != __file__]
    imports = []

    for file in files:
        with open(file) as f_:
            lines = f_.readlines()

        file_imports = [line.rstrip() for line in lines if 'import' in line]
        imports.append(file_imports)
    imports = sum(imports, [])

    v = list(sys.version_info)[:3]
    py_version = '.'.join([str(x) for x in v][:-1])
    try:
        std_libraries = stdlib_list(py_version)
    except ValueError:
        std_libraries = stdlib_list(
            '3.9')  # Defaulting to standard libraries in 3.9

    modules = []

    for statement in imports:
        if not statement.startswith('from'):
            module = statement.split('import ')[-1]
        else:
            module = [x.split('import ')
                      for x in statement.split('from ')][1][0].rstrip()
        if '.' in module:
            module = module.split('.')[0]
        if ' as ' in module:
            module = module.split(' as ')[0]
        if module not in sum([local_modules, std_libraries, modules], []):
            modules.append(module)

    req = {}
    notfound = []

    if manual_version_lookup:
        pip_parent_folder = str(Path(sys.executable).parent)
        if Path(pip_parent_folder + '/pip3').exists():
            pip_path = pip_parent_folder + '/pip3'
        else:
            pip_path = pip_parent_folder + '/pip'

        for module in modules:
            version_res = os.popen(
                f'{pip_path} show {module} | grep Version:').read()
            version_num = version_res.rstrip().split('Version: ')[-1]
            req.update({module: version_num})
    else:
        for module in modules:
            try:
                if args.no_version:
                    req.update({module: ''})
                else:
                    req.update({module: version(module)})
            except PackageNotFoundError:
                logging.warning(
                    f'Could not find: `{module}`! Will attempt to search '
                    f'manually and pick the best candidate...'
                )
                lookup_res = os.popen(
                    f'pip list | grep {module}').read().rstrip().split(' ')
                if lookup_res[0] != '':
                    logging.info(
                        f'Found `{lookup_res[0]}`! Appending to the '
                        f'requirements file...'
                    )
                    req.update({lookup_res[0]: lookup_res[-1]})
                else:
                    logging.warning(
                        f'Failed to find a candidate for `{module}`')
                    notfound.append(module)

    if notfound:
        logging.warning('Could not find:')
        for x in notfound:
            logging.warning(f'    - {x}')
        logging.warning(
            'The name to import the package and the name to install it might '
            'be different... Add these package(s) to the requirements file '
            'manually.'
        )
    return req


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s | %(message)s')
    parser = argparse.ArgumentParser(
        description='Create a requirements.txt file from a project directory')
    parser.add_argument('path', type=str, help='Path to the project directory')
    parser.add_argument('-s',
                        '--specifier',
                        default='>=',
                        type=str,
                        choices=['>=', '==', '~='],
                        help='Version specifier')
    parser.add_argument('-nv',
                        '--no-version',
                        action='store_true',
                        help='Appends package name without its version')
    args = parser.parse_args()

    if sys.argv[1] == '.':
        proj_dir = str(Path.cwd())
    elif Path(sys.argv[1]).exists():
        proj_dir = sys.argv[1]
    else:
        proj_dir = args.path
    assert Path(proj_dir).is_dir()

    req_dict = main(proj_dir)
    if args.no_version:
        req_file = [f'{k}\n' for k, v in req_dict.items()]
    else:
        req_file = [f'{k}{args.specifier}{v}\n' for k, v in req_dict.items()]

    with open(f'{args.path}/requirements.txt', 'w') as f:
        f.writelines(req_file)

    print(f'\nCreated file:\n    {args.path}/requirements.txt\n')
