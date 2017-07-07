from setuptools import find_packages, setup

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
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlalchemy',
        'unrest',
    ],
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements}
)
