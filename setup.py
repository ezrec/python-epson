#!/usr/bin/env python

from distutils.core import setup

setup(
        name='escpr',
        verison='0.0.1',
        description='Python library to manipulate ESC/P Raster Printers',
        license='MIT',
        url='https://github.com/ezrec/python-escprr',
        download_url='https://github.com/ezrec/python-escpr.git',
        long_description=open('README.rst').read(),
        author='Jason S. McMullan',
        author_email='jason.mcmullan@gmail.com',
        platforms=['linux'],
        packages=['escpr'],
        package_data={'': []},
        install_requires=[
            'usb',
            ],
        classifiers=[
            'Development Status :: 1 - Alpha',
            'License :: OSI Approved :: MIT',
            'Operating System :: GNU/Linux',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Topic :: System :: Peripherals',
            'Topic :: Software Development :: Libraries :: Python Modules'
            ],
        )

