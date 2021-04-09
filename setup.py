#!/usr/bin/env python
from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='TwitScraper',
    version='0.1',
    description='Python module to scrape stocktwits',
    long_description=read('README.md'),
    url='https://github.com/Durendal/TwitScraper',
    py_modules=['twitscraper'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
)