#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import sys
import os
import imp

PY3 = (3, 0) <= sys.version_info < (4, 0)


def get_version():
    """Get version and version_info without importing the entire module."""

    devstatus = {
        'alpha': '3 - Alpha',
        'beta': '4 - Beta',
        'candidate': '4 - Beta',
        'final': '5 - Production/Stable'
    }
    path = os.path.join(os.path.dirname(__file__), 'rummage', 'rummage')
    fp, pathname, desc = imp.find_module('__version__', [path])
    try:
        v = imp.load_module('__version__', fp, pathname, desc)
        return v.version, devstatus[v.version_info[3]]
    finally:
        fp.close()


def download_unicodedata():
    """Download the unicodedata version for the given Python version."""

    import unicodedata

    fail = False
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unidatadownload', [path])
    try:
        unidatadownload = imp.load_module('unidatadownload', fp, pathname, desc)
        unidatadownload.download_unicodedata(unicodedata.unidata_version)
    except Exception as e:
        print(e)
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed to download unicodedata!"


def generate_unicode_table():
    """Generate the unicode table for the given Python version."""

    fail = False
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unipropgen', [path])
    try:
        unipropgen = imp.load_module('unipropgen', fp, pathname, desc)
        unipropgen.build_unicode_property_table(
            os.path.join(
                os.path.dirname(__file__),
                'rummage', 'rummage', 'rumcore', 'backrefs', 'uniprops.py'
            )
        )
    except Exception as e:
        print(e)
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed uniprops.py generation!"


VER, DEVSTATUS = get_version()
download_unicodedata()
generate_unicode_table()


LONG_DESC = '''
Rummage is a CLI and GUI tool for searching and replacing texst in files.
It is built with wxPython 3.0.0+ and requires Python 2.7 or Python 3.0 for command line.

The project repo is found at: https://github.com/facelessuser/Rummage.
'''

if PY3:
    entry_points = {
        'console_scripts': [
            'rumcl=rummage.cli:main',
            'rumcl%d.%d=rummage.cli:main' % sys.version_info[:2],
        ]
    }
else:
    entry_points = {
        'gui_scripts': [
            'rummage=rummage.__main__:main'
        ],
        'console_scripts': [
            'rumcl=rummage.cli:main',
            'rumcl%d.%d=rummage.cli:main' % sys.version_info[:2],
        ]
    }

setup(
    name='Rummage',
    version=VER,
    keywords='grep search find',
    description='A gui file search app.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/Rummage',
    packages=find_packages(exclude=[]),
    install_requires=[
        "gntp>=1.0.2",
        "chardet>=2.3.0"
    ],
    zip_safe=False,
    entry_points=entry_points,
    package_data={
        'rummage.rummage.data': ['*.css', '*.js', '*.png', '*.ico', '*.icns']
    },
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
