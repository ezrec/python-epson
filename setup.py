#!/usr/bin/env python3

import io
from distutils.core import setup

setup(
        name='epson',
        version='0.0.1',
        description='Python library to manipulate EPSON ESC/P Printers',
        license='MIT',
        url='https://github.com/ezrec/python-epson',
        download_url='https://github.com/ezrec/python-epson.git',
        long_description=io.open('README.rst').read(),
        author='Jason S. McMullan',
        author_email='jason.mcmullan@gmail.com',
        platforms=['linux'],
        packages=['epson'],
        package_data={'': []},
        classifiers=[
            'Development Status :: 1 - Alpha',
            'License :: OSI Approved :: MIT',
            'Operating System :: GNU/Linux',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3',
            'Topic :: System :: Peripherals',
            'Topic :: Software Development :: Libraries :: Python Modules'
            ],
        )

