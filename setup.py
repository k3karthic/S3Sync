#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from setuptools import setup

setup(
    name='S3Sync',
    version='0.1.0',
    author='Karthic Kumaran',
    author_email='k3.karthic@live.com',
    packages=['s3sync'],
    url='https://github.com/k3karthic/S3Sync',
    license='MIT',
    description='Sync your files to Amazon S3',
    long_description=open('README.txt').read(),
    install_requires=[
        "botocore >= 0.46.0",
        "six >= 1.5.2",
    ],
    entry_points={
        'console_scripts': [
            's3sync=s3sync.cli:main'
        ]
    },
    include_package_data=True
)
