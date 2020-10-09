#!/usr/bin/env python
"""The setup script."""
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
]

test_requirements = [
    'pytest>=3',
]

docs_requires = [
    "sphinx",
]

extras_requires = {
    "test": test_requirements,
    "docs": docs_requires,
    "dev": test_requirements+docs_requires,
}

setup(
    author="Faris A Chugthai",
    author_email='farischugthai@gmail.com',
    description="Directory symlinker",
    entry_points={
        'console_scripts': [
            'dlink=dlink.core:main',
        ],
    },
    extras_require=extras_requires,
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='dlink',
    name='dlink',
    packages=find_packages(
        include=[
            'dlink',
            ]),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/farisachugthai/dlink',
    version='0.1.0',
)
