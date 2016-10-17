import io
import sys
from setuptools import setup, find_packages

version = "0.6.0"

install_requires = []

if sys.version_info < (3, 0):
    with open('requirements2.txt') as fp:
        required = fp.readlines()
        install_requires.extend(required)
else:
    with open('requirements3.txt') as fp:
        required = fp.readlines()
        install_requires.extend(required)

setup(
    name='sevenbridges-python',
    version=version,
    description='SBG API python client bindings',
    install_requires=install_requires,
    long_description=io.open('README.rst', 'r').read(),
    platforms=['Windows', 'POSIX', 'MacOS'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='developer@sbgenomics.com',
    url='https://github.com/sbg/sevenbridges-python',
    license='Apache Software License 2.0',
    include_package_data=True,
    packages=find_packages(exclude=["*.tests"]),
    keywords=['sevenbridges', 'sbg', 'api', 'cgc', 'cancer', 'genomics',
              'cloud'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
