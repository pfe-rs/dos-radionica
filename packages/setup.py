#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='dos-radionica',
    description='Paketi za vežbe iz digitalne obrade signala',
    version='0.1.0',
    author='PFE',
    author_email='kontakt@pfe.rs',
    packages=find_packages(include=[
        'dtmf'
    ]),
    package_data={'': ['*.*']},
    license='../../LICENSE',
    install_requires=['numpy', 'scipy', 'matplotlib'],
)
