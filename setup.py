import codecs
import os.path
from setuptools import find_packages, setup

NAME = 'pydcm2niix'
version = open(os.path.join(NAME, 'VERSION')).read().strip()


with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=NAME,
    version=version,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    author='Jon Stutters',
    author_email='j.stutters@ucl.ac.uk',
    description='Python module for interacting with dcm2niix',
    long_description=long_description,
    url='',
    install_requires=['pydicom'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license='MIT',
    classifiers=[]
)
