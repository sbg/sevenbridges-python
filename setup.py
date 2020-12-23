from pathlib import Path

from setuptools import setup, find_packages
from sevenbridges.version import __version__

setup(
    name='sevenbridges-python',
    version=__version__,
    description='SBG API python client bindings',
    install_requires=Path('requirements.txt').read_text().split(),
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    platforms=['Windows', 'POSIX', 'MacOS'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='dejan.knezevic@sbgenomics.com',
    url='https://github.com/sbg/sevenbridges-python',
    license='Apache Software License 2.0',
    include_package_data=True,
    packages=find_packages(exclude=["tests"]),
    keywords=[
        'sevenbridges', 'sbg', 'api', 'cgc',
        'cancer', 'genomics', 'cloud',
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
