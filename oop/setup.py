# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='otus-log-analyzer',
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    tests_require=[
        'flask-testing',
    ],
    test_suite='tests.suite',
)