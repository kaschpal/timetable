#!/usr/bin/env python3

__license__ = 'MIT'

import argparse
import json
import hashlib
import os
import subprocess
import tempfile
import urllib.request
import shlex
from collections import OrderedDict


parser = argparse.ArgumentParser()
parser.add_argument('packages', nargs='*')
parser.add_argument('--python2', action='store_true',
                    help='Look for a Python 2 package')
parser.add_argument('--cleanup', choices=['scripts', 'all'],
                    help='Select what to clean up after build')
parser.add_argument('--requirements-file',
                    help='Specify requirements.txt file')
parser.add_argument('--build-only', action='store_const',
                    dest='cleanup', const='all',
                    help='Clean up all files after build')
parser.add_argument('--output',
                    help='Specify output file name')
opts = parser.parse_args()


def get_pypi_url(name: str, filename: str) -> str:
    url = 'https://pypi.org/pypi/{}/json'.format(name)
    print('Extracting download url for', name)
    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read().decode('utf-8'))
        for release in body['releases'].values():
            for source in release:
                if source['filename'] == filename:
                    return source['url']
        else:
            raise Exception('Failed to extract url from {}'.format(url))


def get_package_name(filename: str) -> str:
    if filename.endswith(('bz2', 'gz', 'xz', 'zip')):
        segments = filename.split("-")
        if len(segments) == 2:
            return segments[0]
        return "-".join(segments[:len(segments) - 1])
    elif filename.endswith('whl'):
        segments = filename.split("-")
        if len(segments) == 5:
            return segments[0]
        return "-".join(segments[:len(segments) - 4])
    else:
        raise Exception(
            'Downloaded filename: {} does not end with bz2, gz, xz, zip, or whl'.format(filename)
        )

def get_file_hash(filename: str) -> str:
    sha = hashlib.sha256()
    print('Generating hash for', filename)
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1024 * 1024 * 32)
            if not data:
                break
            sha.update(data)
        return sha.hexdigest()


if not opts.packages and not opts.requirements_file:
    exit("Please specifiy either packages or requirements file argument")

packages = []
if opts.requirements_file and os.path.exists(opts.requirements_file):
    with open(opts.requirements_file, 'r') as req_file:
        packages = [package.strip() for package in req_file.readlines()]
else:
    packages = opts.packages


if opts.python2:
    pip_executable = 'pip2'
    pip_install_prefix = '--install-option="--prefix=${FLATPAK_DEST}"'
else:
    pip_executable = 'pip3'
    pip_install_prefix = '--prefix=${FLATPAK_DEST}'

modules = []

for package in packages:
    package_name = 'python{}-{}'.format('2' if opts.python2 else '3',
                                        package.split("=")[0])
    tempdir_prefix = 'pip-generator-{}-'.format(package_name)
    with tempfile.TemporaryDirectory(prefix=tempdir_prefix) as tempdir:

        pip_download = [
            pip_executable,
            'download',
            '--dest',
            tempdir
        ]
        pip_command = [
            pip_executable,
            'install',
            '--no-index',
            '--find-links="file://${PWD}"',
            pip_install_prefix,
            shlex.quote(package)
        ]
        module = OrderedDict([
            ('name', package_name),
            ('buildsystem', 'simple'),
            ('build-commands', [' '.join(pip_command)]),
            ('sources', []),
        ])

        if opts.cleanup == 'all':
            module['cleanup'] = ['*']
        elif opts.cleanup == 'scripts':
            module['cleanup'] = ['/bin', '/share/man/man1']

        try:
            # May download the package twice, the first time it allows pip to
            # select the preferred package, if the package downloaded is not
            # platform generic, then it forces pip to download the sdist (using
            # the --no-binary option).
            subprocess.run(pip_download + [package], check=True)
            for filename in os.listdir(tempdir):
                name = get_package_name(filename)
                if not filename.endswith(('gz', 'any.whl')):
                    os.remove(os.path.join(tempdir, filename))
                    subprocess.run(pip_download + [
                        '--no-binary', ':all:', name
                    ], check=True)
            for filename in os.listdir(tempdir):
                name = get_package_name(filename)
                if name == 'setuptools':  # Already installed
                    continue
                sha256 = get_file_hash(os.path.join(tempdir, filename))
                url = get_pypi_url(name, filename)
                source = OrderedDict([
                    ('type', 'file'),
                    ('url', url),
                    ('sha256', sha256),
                ])
                module['sources'].append(source)
        except subprocess.CalledProcessError:
            print("Failed to download {}".format(package))
            print("Please fix the module manually in the generated file")
        modules.append(module)

if opts.requirements_file:
    output_package = opts.output or 'pypi-dependencies'
else:
    output_package = opts.output or package_name
output_filename = output_package + '.json'

if len(modules) == 1:
    pypi_module = modules[0]
else:
    pypi_module = {
        'name': output_package,
        'buildsystem': 'simple',
        'build-commands': [],
        'modules': modules,
    }

with open(output_filename, 'w') as output:
    output.write(json.dumps(pypi_module, indent=4))
