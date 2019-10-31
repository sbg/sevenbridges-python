import io
import sys

from setuptools import setup, find_packages
from sevenbridges.version import __version__

install_requires = ["requests>=2.20.0", "six>=1.10.0"]
if sys.version_info < (3,):
    install_requires.append("futures>=3.0.4")

setup(
    name='sevenbridges-python',
    version=__version__,
    description='SBG API python client bindings',
    install_requires=install_requires,
    long_description=io.open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    platforms=['Windows', 'POSIX', 'MacOS'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='dejan.knezevic@sbgenomics.com',
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
