import os.path
from setuptools import find_packages, setup

NAME = ''
version = open(os.path.join(NAME, 'VERSION')).read().strip()


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name=NAME,
    version=version,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    author='Jon Stutters',
    author_email='',
    description='',
    long_description=readme(),
    url='',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license='MIT',
    classifiers=[]
)