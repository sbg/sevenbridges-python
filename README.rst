sevenbridges-python
===================

|PyPI version| |Documentation| |Licence|

`CHANGESETS <CHANGES.md>`__

sevenbridges-python is a `Python <http://www.python.org/>`__ library
that provides an interface for `the Seven Bridges
Platform <https://www.sbgenomics.com/>`__ and `Cancer Genomics
Cloud <http://www.cancergenomicscloud.org/>`__ public APIs. It works
with Python versions 2.6+ and supports Python 3.

The `Seven Bridges Platform <https://www.sbgenomics.com/>`__ is a
cloud-based environment for conducting bioinformatic analyses. It is a
central hub for teams to store, analyze, and jointly interpret their
bioinformatic data. The Platform co-locates analysis pipelines alongside
the largest genomic datasets to optimize processing, allocating storage
and compute resources on demand.

The `The Cancer Genomics Cloud
(CGC) <http://www.cancergenomicscloud.org/>`__, powered by `Seven
Bridges <https://www.sbgenomics.com/>`__, is also a cloud-based
computation environment. It was built as one of three pilot systems
funded by the `National Cancer Institute <http://www.cancer.gov/>`__ to
explore the paradigm of colocalizing massive genomics datasets, like The
`Cancer Genomics Atlas (TCGA) <http://cancergenome.nih.gov/>`__,
alongside secure and scalable computational resources to analyze them.
The CGC makes more than a petabyte of multi-dimensional data available
immediately to authorized researchers. You can add your own data to
analyze alongside TCGA using predefined analytical workflows or your own
tools.

Installation
------------

The easiest way to install sevenbridges-python is using pip. :

::

    $ pip install sevenbridges-python

Get the Code
------------

sevenbridges-python is actively developed on GitHub, where the code is
always available.

The easiest way to obtain the source is to clone the public repository :

::

    $ git clone git://github.com/sbg/sevenbridges-python.git

Once you have a copy of the source, you can embed it in your Python
package, or install it into your site-packages by invoking: :

::

    $ python setup.py install

If you are interested in reviewing this documentation locally, clone
this repository, position yourself in the docs directory and after
installing requirements-dev.txt, invoke: :

::

    $ make html

Run Tests
---------

In order to run tests clone this repository, position yourself in the
root of the cloned project and after installing requirements-dev.txt,
invoke: :

::

    py.test

Authentication and Configuration
--------------------------------

In order to authenticate with the API, sevenbridges-python library
requires that you pass in your authentication token and the URL endpoint
for the environment you are working in: either the Seven Bridges
Platform or the Cancer Genomics Cloud.

You can find your authentication token on the respective platform pages:

-  https://igor.sbgenomics.com/developers - for the Seven Bridges
   Platform
-  https://cgc.sbgenomics.com/developers - for the CGC

    The API endpoints for the platforms are:

-  https://api.sbgenomics.com/v2 for the Seven Bridges Platform
-  https://cgc-api.sbgenomics.com/v2 for the CGC

The API documentation is available:

-  http://docs.sevenbridges.com/docs/the-api for the Seven Bridges
   Platform.
-  http://docs.cancergenomicscloud.org/docs/the-cgc-api for the CGC

Initialize configuration using the configuration file
-----------------------------------------------------

Once you obtain your authentication token you can pass it to the Config
object. You can instantiate your API object by passing the appropriate
configuration. There are three ways you can pass configure the library:

1. Pass parameters ``url`` and ``token`` explicitly when initializing
   the config object.
2. Put the API endpoint and token in the environment variables
   ``API_URL`` and ``AUTH_TOKEN`` respectively.
3. Use the configuration file ``$HOME/.sbgrc`` with defined parameters.

Explicit initialization
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import sevenbridges as sbg
    api_config = sbg.Config(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>')

Initialization via environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import sevenbridges as sbg

    import os

    # Usually these would be set in the shell beforehand
    os.environ['API_URL'] = 'https://api.sbgenomics.com/v2'
    os.environ['AUTH_TOKEN'] = '<TOKEN_HERE>'

    api_config = sbg.Config()

Initialization via config file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import sevenbridges as sbg
    api_config = sbg.Config(profile='my-profile')

Notes on config file format
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``.sbgrc`` file has a simple .ini file format, for example:

::

    [my-profile]
    api-url = https://api.sbgenomics.com/v2
    auth-token = <TOKEN_HERE>

    [py-profile-cgc]
    api-url = https://api.sbgenomics.com/v2
    auth-token = <TOKEN_HERE>

Initializing the sevenbridges-python library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The API object represents the central resource for querying, saving and
performing all other actions on your resources. Once you have
instantiated the configuration class, pass it to the API class
constructor.

.. code:: python

    import sevenbridges as sbg
    api_config = sbg.Config()  # Or any other choice of initialization method
    api = sbg.Api(config=api_config)

Examples
--------

The following code illustrates the way the library should be used. For
more detailed examples consult the documentation, hosted on readthedocs.

.. code:: python

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

.. |PyPI version| image:: https://badge.fury.io/py/sevenbridges-python.svg
   :target: https://pypi.python.org/pypi/sevenbridges-python
.. |Documentation| image:: https://readthedocs.org/projects/sevenbridges-python/badge/?version=latest
   :target: http://sevenbridges-python.readthedocs.org/en/latest/
.. |Licence| image:: https://img.shields.io/badge/licence-Apache-orange.svg
   :target: https://github.com/sbg/sevenbridges-python/blob/master/LICENCE
