sevenbridges-python
===================

[![Travis](https://travis-ci.org/sbg/sevenbridges-python.svg)](https://travis-ci.org/sbg/sevenbridges-python)
[![PyPI version](https://badge.fury.io/py/sevenbridges-python.svg)](https://pypi.python.org/pypi/sevenbridges-python)
[![Documentation](https://readthedocs.org/projects/sevenbridges-python/badge/?version=latest)](http://sevenbridges-python.readthedocs.org/en/latest/)
[![Licence](https://img.shields.io/badge/licence-Apache-orange.svg)](https://github.com/sbg/sevenbridges-python/blob/develop/LICENCE)

[CHANGESETS](https://github.com/sbg/sevenbridges-python/blob/develop/CHANGES.md)

sevenbridges-python is a [Python](http://www.python.org/) library that
provides an interface for the [Seven Bridges Platform](https://www.sbgenomics.com/) the
[Cancer Genomics Cloud](http://www.cancergenomicscloud.org/) and
[Cavatica](http://www.cavatica.org) public APIs. It works with Python
versions 2.6+ and supports Python 3.

The [Seven Bridges Platform](https://www.sbgenomics.com/) is a
cloud-based environment for conducting bioinformatic analyses. It is a
central hub for teams to store, analyze, and jointly interpret their
bioinformatic data. The Platform co-locates analysis pipelines alongside
the largest genomic datasets to optimize processing, allocating storage
and compute resources on demand.

The [The Cancer Genomics Cloud (CGC)](http://www.cancergenomicscloud.org/), powered by
[Seven Bridges](https://www.sbgenomics.com/), is also a cloud-based computation
environment. It was built as one of three pilot systems funded by the
[National Cancer Institute](http://www.cancer.gov/) to explore the
paradigm of colocalizing massive genomics datasets, like The
[Cancer Genomics Atlas (TCGA)](http://cancergenome.nih.gov/), alongside secure
and scalable computational resources to analyze them. The CGC makes more
than a petabyte of multi-dimensional data available immediately to
authorized researchers. You can add your own data to analyze alongside
TCGA using predefined analytical workflows or your own tools.

[Cavatica](http://www.cavatica.org/),
powered by [Seven Bridges](https://www.sbgenomics.com/), is a data analysis and sharing
platform designed to accelerate discovery in a scalable, cloud-based
compute environment where data, results, and workflows are shared among
the world's research community. Cavatica is built in collaboration with
the Children Hospital of Philadelphia and it is focused on pediatric
data.

Documentation
-------------

The latest documentation can be found on [readthedocs](http://sevenbridges-python.readthedocs.org/en/latest).

Installation
------------

The easiest way to install sevenbridges-python is using pip. :

    $ pip install sevenbridges-python

Get the Code
------------

sevenbridges-python is actively developed on GitHub, where the code is
always available.

The easiest way to obtain the source is to clone the public repository :

    $ git clone git://github.com/sbg/sevenbridges-python.git

Once you have a copy of the source, you can embed it in your Python
package, or install it into your site-packages by invoking: :

    $ python setup.py install

If you are interested in reviewing this documentation locally, clone
this repository, position yourself in the docs directory and after
installing `requirements.txt` (or `requirements2.txt` if using python 2), invoke:

    $ make html

Run Tests
---------

In order to run tests clone this repository, position yourself in the
root of the cloned project and after installing `requirements.txt` (or
`requirements2.txt` if using python 2), invoke:

    $ pytest

Authentication and Configuration
--------------------------------

In order to authenticate with the API, you should pass the following
items to sevenbridges-python:

(a) Your authentication token
(b) The API endpoint you will be interacting with. This is either the
    endpoint for the Seven Bridges Platform or for the Seven Bridges
    Cancer Genomics Cloud (CGC) or for CAVATICA.

You can find your authentication token on the respective pages:

- <https://igor.sbgenomics.com/developer> for the Seven Bridges Platform
- <https://cgc.sbgenomics.com/developer> for the CGC
- <https://cavatica.sbgenomics.com/developer> for Cavatica

The API endpoints for each environment are:

- <https://api.sbgenomics.com/v2> for the Seven Bridges Platform
- <https://cgc-api.sbgenomics.com/v2> for the CGC.
- <https://cavatica-api.sbgenomics.com/v2> for CAVATICA

For more information about the API, including details of the available
parameters for each API call, you should check the API documentation
before using this library:

- <http://docs.sevenbridges.com/docs/the-api> for the Seven Bridges Platform.
- <http://docs.cancergenomicscloud.org/docs/the-cgc-api> for the CGC.
- <http://docs.cavatica.org/docs/the-api> for CAVATICA

Initialize configuration using the configuration file
-----------------------------------------------------

Once you obtain your authentication token you can pass it to the Config
object. You can instantiate your API object by passing the appropriate
configuration. There are three ways you can pass configure the library:

1.  Pass parameters `url` and `token` explicitly when initializing the
    config object.
2.  Put the API endpoint and token in the environment variables
    `API_URL` and `AUTH_TOKEN` respectively.
3.  Use the configuration file `$HOME/.sevenbridges/credentials` with
    defined parameters.

### Explicit initialization

```python
import sevenbridges as sbg
api = sbg.Api(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>')
```

### Initialization via environment variables

```python
import sevenbridges as sbg

import os

# Usually these would be set in the shell beforehand
os.environ['SB_API_ENDPOINT'] = 'https://api.sbgenomics.com/v2'
os.environ['SB_AUTH_TOKEN'] = '<TOKEN_HERE>'

api = sbg.Api()
```

### Initialization via config file

```python
import sevenbridges as sbg
config = sbg.Config(profile='cgc')
api = sbg.Api(config=config)
```

### Notes on config file format

The `$HOME/.sevenbridges/credentials` file has a simple .ini file
format, for example:

    [default]
    api_endpoint = https://api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>

    [cgc]
    api_endpoint = https://cgc-api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>

    [cavatica]
    api_endpoint = https://cavatica-api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>

#### Initializing the sevenbridges-python library

The API object represents the central resource for querying, saving and
performing all other actions on your resources. Once you have
instantiated the configuration class, pass it to the API class
constructor.

```python
import sevenbridges as sbg
api_config = sbg.Config()  # Or any other choice of initialization method
api = sbg.Api(config=api_config)
```

Examples
--------

The following code illustrates the way the library should be used. For
more detailed examples consult the documentation, hosted on readthedocs.

```python
import sevenbridges as sbg

api_config = sbg.Config()  # Or any other choice of initialization method
api = sbg.Api(config=api_config)

# Get current user
user = api.users.me()

# Query your projects
projects = api.projects.query(limit=100)

# Fetch project files
project = projects[0]
files = project.get_files()
```

Contributing
------------

Contributions, bug reports and issues are very welcome.

You can make your own contributions by forking the develop branch of
this repository, making your changes, and issuing pull request on the
develop branch. Contributors should read the [Seven Bridges Notice to Contributors](CONTRIBUTORS_NOTICE.md) and sign the [Seven Bridges Contributor Agreement](https://secure.na1.echosign.com/public/esignWidget?wid=CBFCIBAA3AAABLblqZhAqt_9rHEqy2MggS0uWRmKHUN2HYi8DWNjkgg5N68iKAhRFTy7k2AOEpRHMMorxc_0*)
before submitting a pull request.

Copyright
---------

Copyright (c) 2016-2018 Seven Bridges Genomics, Inc. All rights
reserved.

This project is open-source via the [Apache 2.0 License](http://www.apache.org/licenses/LICENSE-2.0).
