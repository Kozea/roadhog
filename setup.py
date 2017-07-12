#!/usr/bin/env python

import sys

from setuptools import find_packages, setup

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

tests_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-factoryboy',
    'pytest-flake8',
    'pytest-isort',
]

setup(
    name='roadhog',
    author='Kozea',
    packages=find_packages(exclude=['*.eggs']),
    include_package_data=True,
    install_requires=[
        'alembic',
        'flask',
        'sqlalchemy',
        'unrest',
    ],
    setup_requires=pytest_runner,
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements}
)
