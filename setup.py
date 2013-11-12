#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in the LICENSE
# file at the top-level directory of this package.
#
##############################################################################

setup_kwargs = dict(
    name='txwsman',
    version='0.0.1',
    description='Asynchronous Python WSMAN client',
    long_description=open('README.rst').read(),
    license='See LICENSE file',
    author='Zenoss',
    author_email='eedgar@zenoss.com',
    url='https://github.com/zenoss/txwsman',
    packages=['txwsman', 'txwsman.request'],
    package_data={'txwsman.request': ['*.xml']},
    scripts=[ 'scripts/wsman' ])

try:
    from setuptools import setup
    setup_kwargs['install_requires'] = ['twisted', 'pyOpenSSL']
    try:
        import argparse
        if False:
            argparse
    except ImportError:
        setup_kwargs['install_requires'].append('argparse')
    setup(**setup_kwargs)
except ImportError:
    from distutils.core import setup
    setup(**setup_kwargs)
