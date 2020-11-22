# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='Stonk',
    version='0.1.0',
    description='Monkey trading bot',
    author='Shikanime Deva',
    author_email='deva.shikanime@protonmail.com',
    url='https://github.com/shikanime/stonk',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'stonk = stonk.__main__:main',
        ],
    },
    install_requires=[
        "click>=7.0",
        "hermes-python>=0.7.0"
    ],
    setup_requires=[
        'pytest-runner>=2.7',
    ],
    packages=find_packages(exclude=('tests', 'docs'))
)
