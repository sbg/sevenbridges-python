Quickstart
==========

On this page, you'll find a reference for the Seven Bridges API Python client.

We encourage you to consult our other API resources:

* The Seven Bridges Github repository, `okAPI <https://github.com/sbg/okAPI/tree/master/Recipes/SBPLAT>`_, which includes Python example scripts such as recipes (which allow you to perform specific tasks) and tutorials (which will walk you through entire analyses) via the API. These recipes and tutorials make use of the sevenbridges-python bindings below.
* The Seven Bridges API documentation on our `Knowledge Center <http://docs.sevenbridges.com/docs/the-api>`_, which includes a reference collection of API requests to help you get started right away.

Authentication and Configuration
--------------------------------

In order to authenticate with the API, you should pass the following items to sevenbridges-python:

(a) Your authentication token
(b) The API endpoint you will be interacting with. This is either the endpoint for the Seven Bridges Platform or for the Seven Bridges Cancer Genomics Cloud (CGC) or for CAVATICA.

You can find your authentication token on the respective pages:

-  https://igor.sbgenomics.com/developer for the Seven Bridges Platform
-  https://cgc.sbgenomics.com/developer for the CGC
-  https://cavatica.sbgenomics.com/developer for Cavatica

The API endpoints for each environment are:

-  https://api.sbgenomics.com/v2 for the Seven Bridges Platform
-  https://cgc-api.sbgenomics.com/v2 for the CGC.
-  https://cavatica-api.sbgenomics.com/v2 for CAVATICA


.. note:: We will see below how to supply information about your auth token and endpoint to the library.


For more information about the API, including details of the available parameters for each API call, you should check the API documentation before using this library:

-  http://docs.sevenbridges.com/docs/the-api for the Seven Bridges Platform.
-  http://docs.cancergenomicscloud.org/docs/the-cgc-api for the CGC.
-  http://docs.cavatica.org/docs/the-api for CAVATICA


How to use the Quickstart
-------------------------

We recommend that you pay particular attention to the section 'Managing Projects' of this Quickstart, since it contains general information on working with any kind of Platform or CGC resource (projects, files, tasks, etc) via the Python methods available in this library. 


Initializing the library
------------------------

Once you have obtained your authentication token from one of the URLs listed above, you can initialize the :code:`Api` object defined by this library by passing in your authentication token and endpoint. There are three methods to do this. Details of each method are given below:

1. Pass the parameters ``url`` and ``token`` and optional ``proxies`` explicitly when initializing the
   API object.
2. Set the API endpoint and token to the environment variables ``SB_API_ENDPOINT``
   and ``SB_AUTH_TOKEN`` respectively.
3. Use a configuration file ``$HOME/.sevenbridges/credentials`` with the defined credentials parameters. If config is used proxy settings will be read from
   ``$HOME/.sevenbridges/sevenbridges-python/config`` .ini like file for section ``[proxies]``

.. note:: Keep your authentication token safe! It encodes all your credentials on the Platform or CGC. Generally, we recommend storing the token in a configuration file, which will then be stored in your home folder rather than in the code itself. This prevents the authentication token from being committed to source code repositories.



Import the library
~~~~~~~~~~~~~~~~~~
You should begin by importing the API library sevenbridges-python to your python script that will interact with the API:

.. code:: python

    import sevenbridges as sbg

Then, use one of the following three methods to initialize the library:

1. Initialize the library explicitly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The library can be also instantiated explicitly by passing the URL and authentication token
as key-value arguments into the :code:`Api` object.

.. code:: python

    api = sbg.Api(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>')

*Note* - you can initialize several API clients with
different credentials or environments.

2. Initialize the library using environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import os
    
    # Usually these variables would be set in the shell beforehand
    os.environ['SB_API_ENDPOINT'] = '<https://api.sbgenomics.com/v2' # or 'https://cgc-api.sbgenomics.com/v2>' for cgc, or 'https://cavatica-api.sbgenomics.com/v2' for cavatica
    os.environ['SB_AUTH_TOKEN'] = '<TOKEN_HERE>'

    api = sbg.Api()

3. Initialize the library using a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The configuration file, ``$HOME/.sevenbridges/credentials``, has a simple ``.ini`` file format, with
the environment (the Seven Bridges Platform, or the CGC, or Cavatica) indicated in square brackets, as shown:

::

    [default]
    api_endpoint = https://api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>

    [cgc]
    api_endpoint = https://cgc-api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>
    
    [cavatica]
    api_endpoint = https://cavatica-api.sbgenomics.com/v2
    auth_token = <TOKEN_HERE>


The :code:`Api` object is the central resource for querying, saving and
performing other actions on your resources on the Seven Bridges Platform or CGC. Once you have
instantiated the configuration class, pass it to the API class constructor.

.. code:: python

    c = sbg.Config(profile='cgc')
    api = sbg.Api(config=c)

If not profile is set it will use the default profile.

.. note:: if user creates the api object ``api=sbg.Api()`` and does not pass any information the library will first search whether the environment variables are set. If not it will check
          if the configuration file is present and read the ``[default]`` profile. If that also fail it will raise an exception


Advance Access Features
^^^^^^^^^^^^^^^^^^^^^^^

Advance access features are subject to a change. To enable them just pass
the :code:`advance_access=True` flag when instantiating the library

.. code:: python

    api = sbg.Api(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>', advance_access=True)

.. note:: - Advance access features are subject to a change. No guarantee of any sort is given for AA API calls maintainability.

If you fully understand the above mentioned limitation of Advance access features and are certain you want to use the features across your scripts, you can set this in the `$HOME/.sevenbridges/sevenbridges-python/config` configuration file.

    .. code::

        [mode]
        advance_access=True


Proxy configuration
-------------------

Proxy configuration can be supplied in three different ways.

    - explicit initialization

    .. code:: python

     api = sb.Api(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>',
            proxies={'https_proxy':'host:port', 'http_proxy': 'host:port'})

    - environment variables

    .. code:: python

        os.environ['HTTP_PROXY'] = 'host:port'
        os.environ['HTTPS_PROXY'] = 'host:port'

    - `$HOME/.sevenbridges/sevenbridges-python/config` configuration file

    .. code::

        [proxies]
        https_proxy=host:port
        http_proxy=host:port

    - Explicit with config

    .. code::

        config = sb.Config(profile='my-profile',
                           proxies={'https_proxy':'host:port', 'http_proxy': 'host:port'})
        api = sb.Api(config=config)


.. note:: Once you set the proxy, all calls including upload and download will use the proxy settings.


Low level configuration
---------------------------------
For low level library tweaking such as: number of cached connections and number of parallel requests (useful only for multi-thread applications)
there are few useful arguments when instantiating Api.

    - Three arguments are directly exposed from requests library. Argument `pool_connections` is the number of urllib3 connection pools to cache.
      Argument `pool_maxsize` gives ability to constraint maximum number of parallel requests to save in the pool while `pool_block` flag tells
      whether the connection pool should block for connections. More detailed explanation of those arguments can be found
      `here <http://2.python-requests.org/en/master/api/?highlight=pool#requests.adapters.HTTPAdapter>`_.

    .. code:: python

        api = sb.Api(
            pool_connections=<CONN_NUMBER>,
            pool_maxsize=<POOL_SIZE>,
            pool_block=<BLOCK_FLAG>
        )

    - There is a way to throttle number of parallel requests over all connection pools. That is done using `max_parallel_requests` argument.

    .. code:: python

        api = sb.Api(max_parallel_requests=<MAX_PARALLEL>)

.. note::  Changing those values from default could affect performance.


Rate limit
----------

For API requests that require authentication (i.e. all requests, except the call to list possible API paths), you can issue a maximum of 1000
requests per 300 seconds. Note that this limit is generally subject to
change, depending on API usage and technical limits. Your current rate
limit, the number of remaining requests available within the limit, and the time until your limit is reset can be
obtained using your :code:`Api` object, as follows.

.. code:: python

    api.limit
    api.remaining
    api.reset_time


Error Handlers
--------------

Error handler is a callable that accepts the :code:`api` and :code:`response` objects and returns the response object.
They are most useful when additional logic needs to be implemented based on request result.

Example:

.. code::

    def error_handler(api, response):
        # Do something with the response object
        return response


sevenbridges-python library comes bundled with several useful error handlers. The most used ones
are :code:`maintenance_sleeper` and :code:`rate_limit_sleeper` which pause your code execution until the SevenBridges/CGC
public API is in maintenance mode or when the rate limit is breached.


Usage:

.. code::

    from sevenbridges.http.error_handlers import rate_limit_sleeper, maintenance_sleeper
    api = sb.Api(url='https://api.sbgenomics.com/v2', token='<TOKEN_HERE>',
            error_handlers=[rate_limit_sleeper, maintenance_sleeper])


.. note:: Api object instantiated in this way with error handlers attached will be resilient to server maintenance and rate limiting.


Resource
--------

Most objects handled by sevenbridges-python are inherited from the :code:`Resource` model, which contains some basic methods for all inherited resources.

Resources support lazy fetching, so if a Resource is created with an :code:`id` or :code:`href` the client will fetch it from the API when any attribute
is accessed directly (with a dot operator).

All resources contain the ``api`` property which is generally set by the client to be the previously configured default one, but it can be overridden on a Resource level.

All resources implement the following class methods:

- ``get(id='resource_id')`` - Sends a GET request to the API to retrieve the resource

All resources implement the following instance methods:

- ``reload()`` - Re-initializes the resource with it's data from the API server
- ``delete()`` - Sends a DELETE request to the API to delete the resource
- ``field(name='field_name')`` - Reads a field value without lazy fetching


Managing users
--------------

Currently any authenticated user can access his or her information by
invoking the following method:

.. code:: python

    me = api.users.me()

Once you have initialized the library by authenticating yourself, the object :code:`me` will contain your user information. This includes:

::

    me.href
    me.username 
    me.email
    me.first_name
    me.last_name
    me.affiliation
    me.phone
    me.address
    me.city
    me.state
    me.zip_code
    me.country
    me.role

For example, to obtain your email address invoke:

.. code:: python

    me.email

For user management in divisions and teams, the following are available:

.. code:: python

    # All users in division
    users = api.users.query(division='<division_slug>')

    # Division members
    members = api.users.query(division='<division_slug>', role='member')

    # Division admins
    admins = api.users.query(division='<division_slug>', role='admin')

    # Division external collaborators
    external = api.users.query(division='<division_slug>', role='external_collaborator')

    # Teams for a division
    teams = api.teams.query(division='<division_slug>')

    # All teams in division
    teams_all = api.teams.query(division='<division_slug>', list_all=True)

For disabling users:

.. code-block:: python
    user = api.users.get('<username>')
    user.disable()


Managing projects
-----------------

There are several methods on the :code:`Api` object that can help you manage
your projects.

.. note::  If you are not familiar with the project structure of the Seven Bridges Platform and CGC, take a look at their respective documentation: `projects on the CGC <http://docs.cancergenomicscloud.org/docs/projects-on-the-cgc>`_ and `projects on the Seven Bridges Platform <http://docs.sevenbridges.com/docs/projects-on-the-platform>`_.

List Projects - introduction to pagination and iteration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to list your projects, invoke the :code:`api.projects.query` method. This method
follows server pagination and therefore allows pagination parameters
to be passed to it. Passing a pagination parameter controls which resources you are shown. The :code:`offset` parameter controls the
start of the pagination while the :code:`limit` parameter controls the
number of items to be retrieved.


.. note:: See the `Seven Bridges API overview <http://docs.sevenbridges.com/docs/the-api>`_ or the `CGC API overview <http://docs.sevenbridges.com/docs/the-api>`_ for details of how to refer to a project, and for examples of the pagination parameters.

Below is an example of how to get all your projects, using the :code:`query` method and the pagination parameters :code:`offset` of 0 and :code:`limit` of 10.

.. code:: python

    project_list = api.projects.query(offset=0, limit=10)

:code:`project_list` has now been defined to be an object of the type **collection** which acts
just like a regular python list, and so supports
indexing, slicing, iterating and other list functions. All collections
in the sevenbridges-python library have two methods: :code:`next_page` and
:code:`previous_page` which allow you to load the next or previous pagination pages.

There are several things you can do with a **collection** of any kind of
object:

1. The generic query, e.g. ``api.projects.query()``, accepts the pagination parameters :code:`offset` and
   :code:`limit` as introduced above.
2. If you wish to iterate on a complete **collection** use the ``all()`` method,
   which returns an iterator
3. If you want to manually iterate on the **collection** (page by
   page), use ``next_page()`` and ``previous_page()`` methods on the
   collection.
4. You can easily cast the **collection** to the list, so you can re-use it
   later by issuing the standard Python
   ``project_list = list(api.projects.query().all())``.

.. code:: python

    # Get details of my first 10 projects.
    project_list = api.projects.query(limit=10)

.. code:: python

    # Query projects by project name
    project_list = api.projects.query(name=project_name)

.. code:: python

    # Query projects by project category
    project_list = api.projects.query(category=project_category)

.. code:: python

    # List projects that have both tags 'tagA' and 'tagB'
    project_list = api.projects.query(tags=['tagA', 'tagB'])

.. code:: python

    # Iterate through all my projects and print their name and id
    for project in api.projects.query().all():
        print (project.id,project.name)

.. code:: python

    # Get all my current projects and store them in a list
    my_projects = list(api.projects.query().all())

Get details of a single project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can get details of a single project by issuing the ``api.projects.get()`` method
with the parameter ``id`` set to the id of the project in question. Note that this
call, as well as other calls to the API server may raise an exception
which you can catch and process if required.


*Note* - To process errors from the library,
import :code:`SbgError` from ``sevenbridges.errors``, as shown below.

.. code:: python

    from sevenbridges.errors import SbgError
    try:
        project_id = 'doesnotexist/forsure'
        project = api.projects.get(id=project_id)
    except SbgError as e:
        print (e.message)

Errors in ``SbgError`` have the properties
``code`` and ``message`` which refer to the number and text of 4-digit API status codes that are specific to the Seven Bridges Platform and API. To see all the available codes, see the documentation:

-  http://docs.sevenbridges.com/docs/api-status-codes for the Seven Bridges
   Platform

-  http://docs.cancergenomicscloud.org/docs/api-status-codes for the
   CGC.

Project properties
~~~~~~~~~~~~~~~~~~

Once you have obtained the :code:`id` of a Project instance, you can see its properties. All projects have the following properties:


``href`` - Project href on the API 

``id`` - Id of the project

``name`` - name of the project

``description`` - description of the project

``billing_group`` - billing group attached to the project

``type`` - type of the project (v1 or v2)

``tags`` - list of project tags

``root_folder`` - Id of project's root folder

``settings`` - Project settings

``created_by`` - Project creator

``created_on`` - Date of creation

``modified_on`` - Modification date

The property href :code:`href` is a URL on the server that uniquely identifies the
resource in question. All resources have this attribute. Each project also
has a name, identifier, description indicating its use, a type, some tags and also a
billing\_group identifier representing the billing group that is
attached to the project.



Project methods -- an introduction to methods in the sevenbridges-python library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two types of methods in the sevenbridges-python library: static
and dynamic. Static methods are invoked on the :code:`Api` object instance.
Dynamic methods are invoked from the instance of the object representing the resource (e.g. the project).

Static methods include:

1. Create a new resource: for example,
   ``api.projects.create(name="My new project", billing_group='296a98a9-424c-43f3-aec5-306e0e41c799')``
   creates a new resource. The parameters used will depend on the resource in
   question.
2. Get a resource: the method ``api.projects.get(id='user/project')`` returns details of a
   specific resource, denoted by its id.
3. Query resources - the method ``api.projects.query()`` method returns a pageable
   list of type ``collection`` of projects. The same goes for other resources, so
   ``api.tasks.query(status='COMPLETED')`` returns a **collection** of
   completed tasks with default paging.

Dynamic methods can be generic (for all resources) or specific to a single resource. They
are called on a concrete object, such as a ``Project`` object.

So, suppose that ``project`` is an instance of ``Project`` object. Then, we can:

1. Delete the resource: ``project.delete()``  deletes the object (if deletion of this resource is supported
   on the API).
2. Reload the resource from server: ``project.reload()`` reloads the state of
   the object from the server.
3. Save changes to the server: ``project.save()`` saves all properties

The following example shows some of the methods used to manipulate projects.

.. code:: python

    # Get a collection of projects
    projects = api.projects.query()
    
    # Grab the first billing group 
    bg = api.billing_groups.query(limit=1)[0]
    
    # Create a project using the billing group grabbed above
    new_project = api.projects.create(name="My new project", billing_group=bg.id)
    
    # Add a new member to the project
    new_project.add_member(user='newuser', permissions= {'write':True, 'execute':True})

Other project methods include:

1. Get members of the project and their permissions -
   ``project.get_members()`` - returns a ``Collection`` of members and
   their permissions
2. Add a member to the project - ``project.add_member()``
3. Add a team member to the project - ``project.add_member_team()``
4. Add a division member to the project - ``project.add_member_division()``
5. Remove a member from the project - ``project.remove_member()``
6. List files from the project - ``project.get_files()``
7. Add files to the project - ``project.add_files()`` - you can add a
   single ``File`` or a ``Collection`` of files
8. List apps from the project - ``project.get_apps()``
9. List tasks from the project - ``project.get_tasks()``


Managing datasets
-----------------

The Cavatica Datasets API functionality is an advance access feature which
allows you to manage datasets and their members using dedicated API calls.

The following operations are supported:

    - ``query()`` - Query all datasets
    - ``get_owned_by()`` - Get all datasets owned by a provided user
    - ``get()`` - Get dataset with the provided id
    - ``save()`` - Save changes to a dataset
    - ``delete()`` - Delete dataset
    - ``get_members()`` - Get all members of a dataset
    - ``get_member()`` - Get details on a member of a dataset
    - ``add_member()`` - Add a member to a dataset
    - ``remove_member()`` - Remove member from a dataset

Dataset properties
~~~~~~~~~~~~~~~~~~

Each dataset has the following properties:

``href`` - The URL of the dataset on the API server.

``id`` - Dataset identifier.

``name`` - Dataset name.

``description`` - Dataset description.


Member permissions
~~~~~~~~~~~~~~~~~~

Dataset permissions can be accessed and edited directly on the member object.

Examples
~~~~~~~~

.. code:: python

    # List all public datasets
    datasets = api.datasets.query(visibility='public')

    # List all datasets owned by user
    datasets = api.datasets.query()

    # List datasets by owner
    datasets_by_owner = api.datasets.get_owned_by('dataset_owner')

    # Get details of a dataset
    dataset = api.datasets.get('dataset_owner/dataset-name')

    # List members of a dataset
    members = dataset.get_members()

    # Get details of a dataset member
    member = dataset.get_member('dataset_member')

    # Modify a dataset member's permissions
    member.permissions['execute'] = False
    member.save()

    # Get a dataset member's permissions
    permissions = member.permissions

    # List dataset files
    files = api.files.query(dataset=dataset)

    # Edit a dataset
    dataset.description = 'A new description'
    dataset.save()

    # Remove a dataset member
    dataset.remove_member(member=member)

    # Add a dataset member
    added_member = dataset.add_member(
        username='new_member',
        permissions={
            "write": True,
            "read": True,
            "copy": False,
            "execute": True,
            "admin": False
        }
    )

    # Delete a dataset
    dataset.delete()


Manage billing
--------------

There are several methods on the :code:`Api` object to can help you manage
your billing information. The billing resources that you can interact with are
*billing groups* and *invoices*.

Manage billing groups
~~~~~~~~~~~~~~~~~~~~~

Querying billing groups will return a standard **collection** object.

.. code:: python

    # Query billing groups
    bgroup_list = api.billing_groups.query(offset=0, limit=10)

.. code:: python

    # Fetch a billing group's information
    bg = api.billing_groups.get(id='f1969c90-da54-4118-8e96-c3f0b49a163d')

Billing group properties
~~~~~~~~~~~~~~~~~~~~~~~~

The following properties are attached to each billing group:


``href`` - Billing group href on the API server.
        
``id`` - Billing group identifier.

``owner`` - Username of the user that owns the billing group.

``name`` - Billing group name.

``type`` - Billing group type (free or regular)

``pending`` - True if billing group is not yet approved, False if the billing group has been approved.

``disabled`` - True if billing group is disabled, False if its enabled.

``balance`` - Billing group balance.


Billing group methods
~~~~~~~~~~~~~~~~~~~~~
There is one billing group method:

``breakdown()`` fetches a cost breakdown by project and analysis for the selected billing
group.

Manage invoices
~~~~~~~~~~~~~~~

Querying invoices will return an Invoices **collection** object.

.. code:: python

    invoices = api.invoices.query()

Once you have obtained the invoice identifier you can also fetch specific
invoice information.

.. code:: python

    invoices = api.invoices.get(id='6351830069')

Invoice properties
~~~~~~~~~~~~~~~~~~

The following properties are attached to each invoice.

``href`` - Invoice href on the API server.

``id`` - Invoice identifier.

``pending`` - Set to ``True`` if invoice has not yet been approved by Seven Bridges, ``False`` otherwise.

``analysis_costs`` - Costs of your analysis.

``storage_costs`` - Storage costs.

``total`` - Total costs.

``invoice_period`` - Invoicing period (from-to)


Managing files and folders
--------------------------

Files are an integral part of each analysis. As for as all other resources, the
sevenbridges-python library enables you to effectively query files, in order to retrieve each file's details and metadata. The request to get a file's information can be made in the
same manner as for projects and billing, presented above.

Folders are represented as files with the type "folder".

The available methods for fetching specific files are ``query`` and ``get``:

.. code:: python

    # Query all files in a project
    file_list = api.files.query(project='user/my-project')

.. code:: python

    # Get a single file's information
    file = api.files.get(id='5710141760b2b14e3cc146af')

File properties
~~~~~~~~~~~~~~~

Each file has the following properties:

``href`` - File href on the API server.

``id`` - File identifier.

``type`` - File type.

``name`` - File name.

``size`` - File size in bytes.

``parent`` - Parent folder.

``project`` - Identifier of the project that file is located in.

``created_on`` - Date of the file creation.

``modified_on`` - Last modification of the file.

``origin`` - File origin information, indicating the task that created the file.

``tags`` - File tags.

``metadata`` - File metadata.

File methods
~~~~~~~~~~~~
Files have the following methods:

- Refresh the file with data from the server: ``reload()``
- Copy the file from one project to another: ``copy()``
- Download the file: ``download()``
- Save modifications to the file to the server ``save()``
- Delete the resource: ``delete()``
- List files in folder: ``list_files()``
- Create folder: ``create_folder()``
- Copy file to folder: ``copy_to_folder()``
- Move file to folder: ``move_to_folder()``

See the examples below for information on the arguments these methods take:

Examples
~~~~~~~~

.. code:: python

    # Filter files by name to find only file names containing the specified string:
    files = api.files.query(project='user/my-project')
    my_file = [file for file in files if 'fasta' in file.name]
    
    # Or simply query files by name if you know their exact file name(s)
    files = api.files.query(project='user/myproject', names=['SRR062634.filt.fastq.gz','SRR062635.filt.fastq.gz'])
    my_files = api.files.query(project='user/myproject', metadata = {'sample_id': 'SRR062634'} )

    # Query contents of a folder
    parent = api.files.get('parent_folder_id')
    result = api.files.query(parent=parent)
    
    # Edit a file's metadata
    my_file = my_files[0]
    my_file.metadata['sample_id'] = 'my-sample'
    my_file.metadata['library'] = 'my-library'
    

    # Add metadata (if you are starting with a file without metadata)
    my_file = my_files[0]
    my_file.metadata = {'sample_id' : 'my-sample',
                        'library' : 'my-library'
                      }
                      
    # Also set a tag on that file
    my_file.tags = ['example']
   
    # Save modifications
    my_file.save()
    
    # Copy a file between projects
    new_file = my_file.copy(project='user/my-other-project', name='my-new-file')
    
    # Download a file to the current working directory
    # Optionally, path can contain a full path on local filesystem
    new_file.download(path='my_new_file_on_disk')

    # Get a folder
    folder = api.files.get('file-identifier')

    # List files in a folder
    file_list = folder.list_files()

    # Create folder (with a project or parent identifier)
    new_folder = api.files.create_folder(
        name='new_folder_name', project='project-identifier',
    )
    new_folder = api.files.create_folder(
        name='new_folder_name', parent='parent-folder-identifier'
    )

    # Copy file to folder
    copied_file = my_file.copy_to_folder(
        parent=new_folder, name='new-file-name'
    )

    # Move file to folder
    moved_file = my_file.move_to_folder(
        parent=new_folder, name='new-file-name'
    )

List Files - introduction to pagination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The results of files queries - :code:`api.files.query()` and :code:`api.files.list_files()`, can be paginated
in two ways: using offset or continuation token parameter.

Working with offset pagination is equivalent to that explained in 'List Projects - introduction to pagination and iteration' section,
so one can get informed there about using :code:`offset` and :code:`limit` parameters.

The continuation token pagination can be achieved by using :code:`cont_token` parameter (in combination with :code:`limit`)
in query methods (:code:`query()`/:code:`list_files()`). This parameter is a base64 encoded value, telling server
where to start next page. If one wants to use continuation token pagination, :code:`query()`/:code:`list_files()` method
should be called with :code:`cont_token` parameter, as in example below:

.. code:: python

    files_list = api.files.query(cont_token='init', limit=10)

The :code:`'init'` value is special initial value that should be passed at first call of :code:`query()`/:code:`list_files()`
method if continuation token pagination is desired.

There are certain restrictions on using this parameter:

1. The continuation token pagination is advance access feature, so :code:`cont_token` parameter can be used only if
   :code:`advance_access` is set to :code:`True`, otherwise :code:`SbgError` will be returned.
2. The continuation token pagination cannot be used together with metadata filtering, so if :code:`cont_token` and
   :code:`metadata` parameters are both provided to :code:`query()`/:code:`list_files()`, :code:`SbgError` will be returned.
3. The continuation token pagination and offset pagination are mutually exclusive, so if there are passed both
   :code:`cont_token` and :code:`offset` parameters to :code:`query()`/:code:`list_files()`, :code:`SbgError` will be returned.


Managing file upload and download
---------------------------------

``sevenbridges-python`` library provides both synchronous and asynchronous
way of uploading or downloading files.

File Download
~~~~~~~~~~~~~

Synchronous file download:

.. code:: python

    file = api.files.get('file-identifier')
    file.download('/home/bar/foo/file.bam')

Asynchronous file download:

.. code:: python

    file = api.files.get('file-identifier')
    download = file.download('/home/bar/foo.bam', wait=False)

    download.path # Gets the target file path of the download.
    download.status # Gets the status of the download.
    download.progress # Gets the progress of the download as percentage.
    download.start_time # Gets the start time of the download.
    download.duration # Gets the download elapsed time.

    download.start() # Starts the download.
    download.pause() # Pauses the download.
    download.resume() # Resumes the download.
    download.stop() # Stops the download.
    download.wait() # Block the main loop until download completes.

You can register the callback or error callback function to the
download handle: ``download.add_callback(callback=my_callback, errorback=my_error_back)``

Registered callback method will be invoked on completion of the download. The errorback
method will be invoked if error happens during download.

File Upload
~~~~~~~~~~~

Synchronous file upload:

.. code:: python

    # Get the project or parent folder to where we want to upload files.
    project = api.projects.get('project-identifier')
    api.files.upload('/home/bar/foo/file.fastq', project=project)

    parent_folder = api.files.get('folder-identifier')
    api.files.upload('/home/bar/foo/file.fastq', parent=parent_folder)

    # Optionally we can set file name of the uploaded file.
    api.files.upload('/home/bar/foo/file.fastq', project, file_name='new.fastq')

Asynchronous file upload:

.. code:: python

    upload = api.files.upload('/home/bar/foo/file.fastq', 'project-identifier', wait=False)

    upload.file_name # Gets the file name of the upload.
    upload.status # Gets the status of the upload.
    upload.progress # Gets the progress of the upload as percentage.
    upload.start_time # Gets the start time of the upload.
    upload.duration # Gets the upload elapsed time.

    upload.start() # Starts the upload.
    upload.pause() # Pauses the upload.
    upload.resume() # Resumes the upload.
    upload.stop() # Stops the upload.
    upload.wait() # Block the main loop until upload completes.

You can register the callback or error callback in the same manner as it
was described for asynchronous file download.


Managing volumes: connecting cloud storage to the Platform
----------------------------------------------------------

Volumes authorize the Platform to access and query objects on a specified cloud storage (Amazon Web Services or Google Cloud Storage) on your behalf. As for as all other resources, the sevenbridges-python library enables you to effectively query volumes, import files from a volume to a project or export files from a project to the volume. 

The available methods for listing volumes, imports and exports are ``query`` and ``get``, as for other objects:

.. code:: python

    # Query all volumes
    volume_list = api.volumes.query()
    # Query all imports
    all_imports = api.imports.query()
    # Query failed exports
    failed_exports = api.exports.query(state='FAILED')

.. code:: python

    # Get a single volume's information
    volume = api.volumes.get(id='user/volume')
    # Get a single import's information
    i = api.imports.get(id='08M4ywDZkQuJOb3L5M8mMSvzoeGezTdh')
    # Get a single export's information
    e = api.exports.get(id='0C7T8sBDP6aiNbwvXv12QZFPW55wJ3GJ')


Volume properties
~~~~~~~~~~~~~~~~~

Each volume has the following properties:

``href`` - Volume href on the API server.

``id`` - Volume identifier in format owner/name.

``name`` - Volume name. Learn more about this in our `Knowledge Center <http://docs.sevenbridges.com/docs/volumes#section-volume-name>`_.

``access_mode`` - Whether the volume was created as read-only (RO) or read-write (RW). Learn more about this in our `Knowledge Center <http://docs.sevenbridges.com/docs/volumes#section-access-mode>`_.

``active`` - Whether or not this volume is active.

``created_on`` - Time when the volume was created.

``modified_on`` - Time when the volume was last modified.

``description`` - An optional description of this volume.

``service`` - This object contains the information about the cloud service that this volume represents.

Volume methods
~~~~~~~~~~~~~~

Volumes have the following methods:

-  Refresh the volume with data from the server: ``reload()``
-  Get imports for a particular volume ``get_imports()``
-  Get exports for a particular volume ``get_exports()``
-  Create a new volume based on the AWS S3 service using IAM user as authentication mechanism -  ``create_s3_volume()``
-  Create a new volume based on the AWS S3 service using IAM role as authentication mechanism -  ``create_s3_volume_role_auth()``
-  Create a new volume based on the Google Cloud Storage service  - ``create_google_volume()``
-  Create a new volume based on the Aliyun service - ``create_oss_volume()``
-  Save modifications to the volume to the server ``save()``
-  Unlink the volume ``delete()``
-  Get volume members ``get_members()``
-  Add a member to the project - ``add_member()``
-  Add a team member to the project - ``add_member_team()``
-  Add a division member to the project - ``add_member_division()``
-  List files that belong to a volume - ``list()``


See the examples below for information on the arguments these methods take:

Examples
~~~~~~~~

.. code:: python

    # Create a new volume based on AWS S3 for importing files, with IAM user as auth mechanism
    volume_import = api.volumes.create_s3_volume(
        name='my_input_volume',
        bucket='my_bucket',
        access_key_id='AKIAIOSFODNN7EXAMPLE',
        secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        access_mode='RO'
    )

    # Create a new volume based on AWS S3 for exporting files, with IAM user as auth mechanism
    volume_export = api.volumes.create_s3_volume(
        name='my_output_volume',
        bucket='my_bucket',
        access_key_id='AKIAIOSFODNN7EXAMPLE',
        secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        access_mode='RW'
    )

    # Create a new volume based on AWS S3 for importing files, with IAM role as auth mechanism
    volume_import = api.volumes.create_s3_volume_role_auth(
        name='my_input_volume',
        bucket='my_bucket',
        role_arn='arn:aws:iam::ACCOUNTNUMBER:role/ROLE-NAME',
        external_id = 'external_id',
        access_mode='RO'
    )

    # Create a new volume based on AWS S3 for exporting files, with IAM role as auth mechanism
    volume_export = api.volumes.create_s3_volume(
        name='my_output_volume',
        bucket='my_bucket',
        role_arn='arn:aws:iam::ACCOUNTNUMBER:role/ROLE-NAME',
        external_id = 'external_id',
        access_mode='RW'
    )

    # List all volumes available
    volumes = api.volumes.query()

    # List all files in volume
    file_list = volume.list()

    # The previous call only returns the first page of results, retrieving all
    # files in a volume root directory is done by using 'all'. This does not
    # include files in subdirectories
    for volume_file in volume.list().all():
        print(volume_file)

    # Subdirectories are stored in prefixes
    prefixes = file_list.prefixes

    # Files in first subdirectory
    prefix = prefixes[0].prefix
    file_list_sub = volume.list(prefix=prefix)

Import properties
~~~~~~~~~~~~~~~~~

When you import a file from a volume into a project on the Platform, you are importing a file from your cloud storage provider (Amazon Web Services or Google Cloud Storage) via the volume onto the Platform.

If successful, an alias will be created on the Platform. Aliases appear as files on the Platform and can be copied, executed, and modified as such. They refer back to the respective file on the given volume.

Each import has the following properties:

``href`` - Import href on the API server.

``id`` - Import identifier.

``source`` - Source of the import, object of type ``VolumeFile``, contains info on volume and file location on the volume.

``destination`` - Destination of the import, object of type ``ImportDestination``, containing info on project where the file was imported to and name of the file in the project.

``state`` - State of the import. Can be *PENDING*, *RUNNING*, *COMPLETED* and *FAILED*.

``result`` - If the import was completed, contains the result of the import - a ``File`` object.

``error`` - Contains the ``Error`` object if the import failed.

``overwrite`` - Whether the import was set to overwrite file at destination or not.

``started_on`` - Contains the date and time when the import was started.

``finished_on`` - Contains the date and time when the import was finished.

``preserve_folder_structure`` - Whether to keep the exact source folder structure. The default value is true if the item being imported is a folder. Should not be used if you are importing a file.

``autorename`` - Whether to automatically rename the item (by prefixing its name with an underscore and number) if another one with the same name already exists at the destination.


VolumeFile properties
~~~~~~~~~~~~~~~~~~~~~

``volume`` - Volume ID from which to import the item.

``location`` - Volume-specific location pointing to the file or folder to import. This location should be recognizable to the underlying cloud service as a valid key or path to the item. If the item being imported is a folder, its path should end with a ``/``.


ImportDestination properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``project`` - The project in which to create the alias.

``parent`` - The ID of the target folder to which the item should be imported. Should not be used together with project. If parent is used, the import will take place into the specified folder, within the project to which the folder belongs. If project is used, the items will be imported to the root of the project's files.

``name`` - The name of the alias to create. This name should be unique to the project. If the name is already in use in the project, you should use the overwrite query parameter in this call to force any item with that name to be deleted before the alias is created. If name is omitted, the alias name will default to the last segment of the complete location (including the prefix) on the volume. Segments are considered to be separated with forward slashes ``/``.


Import methods
~~~~~~~~~~~~~~

Imports have the following methods:

-  Refresh the import with data from the server: ``reload()``
-  Start an import  by specifying the source and the destination of the import - ``submit_import()``
-  Delete the import -  ``delete()``

See the examples below for information on the arguments these methods take:

Examples
~~~~~~~~

.. code:: python

    # Import a  file to a project
    my_project = api.projects.get(id='my_project')
    bucket_location = 'fastq/my_file.fastq'
    imp = api.imports.submit_import(volume=volume_import, project=my_project, location=bucket_location)
    # Wait until the import finishes
    while True:
          import_status = imp.reload().state
          if import_status in (ImportExportState.COMPLETED, ImportExportState.FAILED):
               break
          time.sleep(10)
    # Continue with the import
    if imp.state == ImportExportState.COMPLETED:
          imported_file = imp.result


Export properties
~~~~~~~~~~~~~~~~~

When you export a file from a project on the Platform into a volume, you are essentially writing to 
your cloud storage bucket on Amazon Web Services or Google Cloud Storage via the volume.

Note that the file selected for export must not be a public file or an alias. Aliases are objects stored 
in your cloud storage bucket which have been made available on the Platform.

The volume you are exporting to must be configured for read-write access. To do this, set the ``access_mode`` 
parameter to ``RW`` when creating or modifying a volume. Learn more about this from 
our `Knowledge Center <http://docs.sevenbridges.com/docs/volumes#section-access-mode>`_.

If an export command is successful, the original project file will become an alias to the newly exported object 
on the volume. The source file will be deleted from the Platform and, if no more copies of this file exist, 
it will no longer count towards your total storage price on the Platform. Once you export a file from the Platform 
to a volume, it is no longer part of the storage on the Platform and cannot be exported again.

Each export has the following properties:

``href`` - Export href on the API server.

``id`` - Export identifier.

``source`` - Source of the export, object of type ``File``

``destination`` - Destination of the export, object of type ``VolumeFile``, containing info on project where the file was imported to and name of the file in the project

``state`` - State of the export. Can be *PENDING*, *RUNNING*, *COMPLETED* and *FAILED*.

``result`` - If the export was completed, this contains the result of the import - a ``File`` object.

``error`` - Contains the ``Error`` object if the export failed.

``overwrite`` - Whether or not the export was set to overwrite the file at the destination.

``started_on`` - Contains the date and time when the export  was started.

``finished_on`` - Contains the date and time when the export was finished.

Export methods
~~~~~~~~~~~~~~

Exports have the following methods:

-  Refresh the export with data from the server: ``reload()``
-  Submit export, by specifying source and destination of the import: ``submit_import()``
-  Delete the export: ``delete()``

See the examples below for information on the arguments these methods take:


Examples
~~~~~~~~

.. code:: python

    # Export a set of files to a volume
    # Get files from a project
    files_to_export = api.files.query(project=my_project).all()
    # And export all the files to the output bucket
    exports = []
    for f in files_to_export:
          export = api.exports.submit_export(file=f, volume = volume_export, location=f.name)
          exports.append(export)
    # Wait for exports to finish:
    num_exports = len(exports)
    done = False
    
    while not done:
          done_len = 0 
          for e in exports:
                 if e.reload().state in (ImportExportState.COMPLETED, ImportExportState.FAILED):
                        done_len += 1
                 time.sleep(10)
          if done_len == num_exports:
                 done = True


Managing divisions
------------------

Enterprise access to the Platform is available on demand and allows companies or organizations to mimic their internal
structure and hierarchy on the Seven Bridges Platform, thus facilitating simpler and more efficient collaboration.

Enterprise accounts are granted to users through their organizations. The organization associated with the
Enterprise account may create user groups (Divisions and Teams) composed of Enterprise account holders,
which are used to enable collaboration between members of the organization.

A Division on the Platform is a subgroup of users within an Enterprise. Use the Division entity to replicate
the structure and hierarchy of an organization, such as departmental groups on the Platform.
Divisions are created by Enterprise account administrators, but may be assigned Division administrator to manage the
Division.

A Team on the Platform is a subgroup of a Division. Teams may be created by the Division administrator to simplify
adding multiple members to a project simultaneously. One Division member can belong to multiple Teams.

The available methods for listing division are ``query`` and ``get``, as for other objects:

.. code:: python

    # Query all divisions user belongs to (division authentication token required)
    division_collection = api.divisions.query()
    # Get a single division's information
    division = api.divisions.get(id='division-id')


Division properties
~~~~~~~~~~~~~~~~~~~

``id`` - Division ID.

``name`` - Division name. Learn more about this in our `Knowledge Center <https://docs.sevenbridges.com/docs/manage-a-division>`_.

Division methods
~~~~~~~~~~~~~~~~

Divisions have the following methods:

-  Refresh the division with data from the server: ``reload()``
-  Get teams belonging to particular division ``get_teams()``
-  Get user members belonging to particular division ``get_members()``


Managing apps
-------------

Managing apps (tools and workflows) with the sevenbridges-python library is simple. Apps on the Seven
Bridges Platform and CGC are implemented using the Common Workflow Language (CWL)
specification
https://github.com/common-workflow-language/common-workflow-language.

Querying all apps or getting the details of a single app can be done in the same
way as for other resources, using the ``query()`` and ``get`` methods. You
can also invoke the following class-specific methods:

-  ``get_revision()`` - Returns a specific app revision.
-  ``install_app()`` - Installs your app on the server, using its CWL description.
-  ``create_revision()`` - Creates a new revision of the specified app.
-  ``sync()`` - Syncs the parent app changes with the current app instance.
-  ``copy()`` - Copies the current app.

.. note:: Listing public apps can be achieved by invoking ``api.apps.query(visibility='public')``

App properties
~~~~~~~~~~~~~~

Each app has the following properties:

``href`` - The URL of the app on the API server.

``id`` - App identifier.

``name`` - App name.

``project`` - Identifier of the project that app is located in.

``revision`` - App revision.

``raw`` - Raw CWL description of the app.

App methods
~~~~~~~~~~~

- App only has class methods that were mentioned above.

Managing tasks
--------------

Tasks (pipeline executions) are easy to handle using the sevenbridges-python library. As with all
resources you can ``query()`` your tasks, and ``get()`` a single task
instance. You can also do much more. We will outline task properties and
methods and show in the examples how easy is to run your first analysis using Python.

Task properties
~~~~~~~~~~~~~~~

``href`` - Task URL on the API server.

``id`` - Task identifier.

``name`` - Task name.

``status`` - Task status.

``project`` - Identifier of the project that the task is located in.

``app`` - The identifier of the app that was used for the task.

``type`` - Task type.

``created_by`` - Username of the task creator.

``executed_by``- Username of the task executor.

``batch`` - Boolean flag: ``True`` for batch tasks, ``False`` for regular &
child tasks.

``batch_by`` - Batching criteria.

``batch_group`` - Batch group assigned to the child task calculated from
the ``batch_by`` criteria.

``batch_input`` - Input identifier on to which to apply batching.

``parent`` - Parent task for a batch child.

``end_time`` - Task end time.

``execution_settings`` - Execution settings for the task.

``execution_status`` - Task execution status.

``price`` - Task cost.

``inputs`` - Inputs that were submitted to the task.

``outputs`` - Generated outputs from the task.

``origin`` - Id of the entity that created the task, e.g. automation run, if task was created by an automation run


.. note:: Check the documentation on the `Seven Bridges API <http://docs.sevenbridges.com/docs/create-a-new-task>`_ and the `CGC API <http://docs.cancergenomicscloud.org/docs/create-a-new-task>`_ for more details on batching criteria. 



Task methods
~~~~~~~~~~~~
The following class and instance methods are available for tasks:

-  Create a task on the server and, optionally, run it: ``create()``.
-  Query tasks: ``query()``.
-  Get single task's information: ``get()``.
-  Abort a running task: ``abort()``.
-  Run a draft task: ``run()``
-  Delete a draft task from the server: ``delete()``.
-  Refresh the task object information with the date from the server:
   ``refresh()``.
-  Save task modifications to the sever: ``save()``.
-  Get task execution details: ``get_execution_details()``.
-  Get batch children if the task is a batch task:
   ``get_batch_children()``.
-  Clone task and optionally run it: ``clone()``.

Task creation hints
~~~~~~~~~~~~~~~~~~~

- Both input files and parameters are passed the same way together in a single dictionary to ``inputs``.

- Supported execution settings are:
    - `instance_type` - list or a string, can be 'AUTO' or an actual instance type, for example: ['c4.2xlarge;ebs-gp2;2000']
    - `max_parallel_instances` - Number of instances, >= 1


Querying tasks
~~~~~~~~~~~~~~
- ``api.tasks.query`` always return an array of tasks. For single task inputs, use ``api.tasks.query(project='my-project')[0]``.

- Queried tasks can be sorted with the ``order_by`` parameter. Supported fields are ``created_time``, ``start_time``, ``name``, ``end_time``, and ``created_by``.
- Ordering can be specified with the ``order`` parameter. It is set to ``desc`` by default. Ascending order is set with ``asc``.

.. note:: When querying running tasks it is recommended to use ordering, since the results are paginated and it is possible that some tasks will be duplicated or missed.


Task Examples
~~~~~~~~~~~~~

Single task
^^^^^^^^^^^

.. code:: python

    # Task name
    name = 'my-first-task'
    
    # Project in which I want to run a task.
    project = 'my-username/my-project'

    # App I want to use to run a task
    app = 'my-username/my-project/my-app'

    # Inputs
    inputs = {}
    inputs['FastQC-Reads'] = api.files.query(project='my-project', metadata={'sample': 'some-sample'})
    
    try:
        task = api.tasks.create(name=name, project=project, app=app, inputs=inputs, run=True)
    except SbError:
        print('I was unable to run the task.')
    
    # Task can also be ran by invoking .run() method on the draft task.
    task.run()
    
    
Clone a task and run it with modification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it is convenient to take an already executed task and change 
only some of the inputs, to then re-run it, using the clone method.
Note: the clone method has the parameter `run=True` by default, so 
it is important to set it to `False` if modifications are needed.

.. code:: python

    # Getting the old task by id
    old_task = api.tasks.get(old_task_id)
    
    # clone it without launching it.
    new_task = old_task.clone(run=False)
    
    # Modify the inputs
    new_task.inputs['somekey'] = "new value"
    
    # Save the new task, and run it.
    new_task.save()
    new_task.run()

Batch task
^^^^^^^^^^

.. code:: python

    # Task name
    name = 'my-first-task'
    
    # Project in which to run the task.
    project = 'my-username/my-project'
    
    # App to use to run the task
    app = 'my-username/my-project/my-app'

    # Inputs
    inputs = {}
    inputs['FastQC-Reads'] = api.files.query(project=project, metadata={'sample': 'some-sample'})
    
    # Specify that one task should be created per file (i.e. batch tasks by file).
    batch_by = {'type': 'item'}


    # Specify that the batch input is FastQC-Reads
    batch_input = 'FastQC-Reads'

    try:
        task = api.tasks.create(
            name=name, project=project, app=app, inputs=inputs,
            batch_input=batch_input, batch_by=batch_by, run=True
        )
    except SbError:
        print('I was unable to run a batch task.')


Secondary files
^^^^^^^^^^^^^^^

Accessing task input/output secondary files is possible using the secondary_files property on the input/output itself.

Example for outputs:

.. code:: python

    task = api.tasks.get('<task_id>')
    secondary_files = task.outputs['<output_name>'].secondary_files


Managing bulk operations
------------------------

Bulk operations are supported for:

    - Files
    - Import jobs
    - Export jobs

All bulk operations return a list of objects that contain a resource or an
error. The state of any object can be checked with the ``valid`` property. If
``valid`` is set to True, ``resource`` is available, otherwise ``error`` is
populated. Example:

.. code:: python

    response = api.files.bulk_get(files=files)
    for record in response:
        if record.valid:
            print(record.resource)
        else:
            print(record.error)

The maximum number of resources that can be processed in a single bulk call is 100.

Files
~~~~~

The following operations are supported:

    - ``bulk_get()`` - Retrieves multiple files.
    - ``bulk_edit()`` - Modifies the existing information for specified files or add new information while preserving omitted parameters.
    - ``bulk_update()`` - Sets new information for specified files, replacing all existing information and erasing omitted parameters.
    - ``bulk_delete()`` - Deletes multiple files.

Retrieval and deletion are done by passing files (or file ids) in a list:

.. code:: python

    # Retrieve files
    files = ['<FILE_ID>', '<FILE_ID>', '<FILE_ID>']
    response = api.files.bulk_get(files=files)

    # Delete files
    files = [file1, file2, file3]
    response = api.files.bulk_delete(files=files)

Editing and updating are done on file objects:

.. code:: python

    # Edit files
    files = [edited_file1, edited_file2, edited_file3]
    response = api.files.bulk_edit(files=files)

    # Update files
    files = [updated_file1, updated_file2, updated_file3]
    response = api.files.bulk_update(files=files)

Properties that can be edited are ``name``, ``tags`` and ``metadata``.

Tasks
~~~~~

The following operations are supported:

    - ``bulk_get()`` - Retrieves multiple tasks.

Retrieval is done by passing tasks (or task ids) in a list:

.. code:: python

    # Retrieve tasks
    tasks = ['<TASK_ID>', '<TASK_ID>', '<TASK_ID>']
    response = api.tasks.bulk_get(tasks=tasks)

Imports
~~~~~~~

The following operations are supported:

    - ``bulk_get()`` - Retrieves multiple import jobs.
    - ``bulk_submit()`` - Submits multiple import jobs.

Bulk retrieval, similarly to api.files.bulk_get(), requires a list of jobs:

.. code:: python

    # Retrieve imports
    imports = ['<IMPORT_ID>', '<IMPORT_ID>', '<IMPORT_ID>']
    response = api.imports.bulk_get(imports=imports)

Submitting in bulk can be done with a list of dictionaries with the required
data for each job, for example:

.. code:: python

    volume = api.volumes.get('user/volume')
    project = api.project.get('user/project')

    # Submit import jobs
    imports = [
        {
            'volume': volume,
            'location': '/data/example_file.txt',
            'project': project,
            'name': 'example_file.txt',
            'overwrite': False
        },
        {
            'volume': volume,
            'location': '/data/example_file_2.txt',
            'project': project,
            'name': 'example_file_2.txt',
            'overwrite': True
        }
    ]
    response = api.imports.bulk_submit(imports=imports)

Exports
~~~~~~~

The following operations are supported:

    - ``bulk_get()`` - Retrieves multiple export jobs.
    - ``bulk_submit()`` - Submits multiple export jobs.

Bulk retrieval, similarly to api.files.bulk_get(), requires a list of jobs:


.. code:: python

    # Retrieve exports
    exports = ['<EXPORT_ID>', '<EXPORT_ID>', '<EXPORT_ID>']
    response = api.exports.bulk_get(exports=exports)


Submitting in bulk can be done with a list of dictionaries with the required
data for each job, for example:

.. code:: python

    volume = api.volumes.get('user/volume')

    # Find some files to export 
    files_to_export = list(api.files.query(project='user/my-project').all())

    # Create exports list
    # We will be exporting all the files in a project (root folder only) to
    # the volume, with a location same as the name of the file

    exports = []
    
    for file in files_to_export:
          export = {
                'file':file,
                'volume': volume,
                'location':file.name
          }
          exports.append(export)

    response = api.exports.bulk_submit(exports=exports, copy_only=False)


Managing automations
--------------------

The following operations are supported for automations:

    - ``query()`` - Query all automations
    - ``get()`` - Get automation with the provided id
    - ``get_packages()`` - Get all packages of an automation
    - ``get_package()`` - Get package with provided id
    - ``add_package()`` - Add a package to an automation
    - ``archive()`` - Archive an automation
    - ``restore()`` - Restore an archived automation
    - ``get_members()`` - Get all members of an automation
    - ``get_member()`` - Get details on a member of an automation
    - ``add_member()`` - Add a member to an automation
    - ``remove_member()`` - Remove member from an automation
    - ``get_runs()`` - Get automation runs

The following operations are supported for automation packages:
    - ``query()`` - Query all automation packages
    - ``get()`` - Get automation package with the provided id
    - ``create()`` - Create automation package
    - ``archive()`` - Archive an package
    - ``restore()`` - Restore an archived package

The following operations are supported for automation runs:

    - ``query()`` - Query all automation runs
    - ``get()`` - Get automation run with the provided id
    - ``create()`` - Create and start new automation run
    - ``rerun()`` - Reruns an existing automation run
    - ``stop()`` - Stop an automation run
    - ``get_log()`` - Get log file contents for an automation run
    - ``get_state()`` - Get state file contents for an automation run

Properties
~~~~~~~~~~

Each automation has the following properties:

``href`` - The URL of the automation on the API server.

``id`` - Automation identifier.

``name`` - Automation name.

``description`` - Automation description.

``owner`` - Username of the user that owns the automation.

``created_by`` - Username of the user that created the automation.

``created_on`` - Date of the first automation creation.

``modified_by`` - Username of the user that last modified the automation.

``modified_on`` - Date of the last modification of the automation.

Each automation package has the following properties:

``id`` - Automation package identifier.

``automation`` - Identifier of the automation the package belongs to.

``version`` - Automation package version.

``location`` - Location identifier of uploaded automation package.

``created_by`` - Username of the user that created the automation.

``created_on`` - Date of the automation package creation.

``archived`` - Flag indicating wheather automation package is arhived or not.

``custom_url`` - Link to custom frontend page.

Each automation run has the following properties:

``href`` - The URL of the automation run on the API server.

``id`` - Automation identifier.

``automation`` - Automation identifier of the automation the run belongs to.

``package`` - Automation package identifier of the package the run belongs to.

``inputs`` - Automation run input dictionary.

``settings`` - Automation run settings override dictionary.

``created_on`` - Date of the first automation run creation.

``start_time`` - Date of the automation run start.

``end_time`` - Date of the automation run end.

``resumed_from`` - Automation run identifier of the automation run the run resumed from.

``created_by`` - Username of the user that created the automation run.

``status`` - Current status of the automation run.

``message`` - Message output of the automation run.

``execution_details`` - Execution details of the automation run.

Examples
~~~~~~~~

.. code:: python

    # Query automation runs with name parameter
    api.automation_runs.query(name='automation_run_name')

    # List all automations
    automations = api.automations.query()

    # Get details of an automation
    automation = api.automations.get('automation_id')

    # Create automation package from uploaded code package
    automation_package = api.automation_packages.create('automation_id', 'version', 'location_id'):

    # Add a code package to automation from local file
    automation.add_package('version', 'file_path', schema={})

    # Get automation package details
    automation_package = api.automation_packages.get('package_id')

    # Get automation runs with name parameter for existing automation
    automation.get_runs(name='automation_run_name')

    # List all packages that belong to an automation
    packages = automation.get_packages()

    # List all members that belong to an automation
    members = automation.get_members()

    # Get details of an automation member
    member = automation.get_member('member_username')

    # Add new member to automation
    username = 'new_member_username'
    permissions = {
        'read': True,
        'write': True,
        'copy': True,
        'execute': True,
        'admin': True,
    }
    new_member = automation.add_member(username, permissions)

    # Edit member permissions
    new_member.permissions['admin'] = False
    new_member.save()

    # Remove member from automation
    automation.remove_member('automation_member')

    # List automation runs
    runs = api.automation_runs.query()

    # Get details of an automation run
    run = api.automation_runs.get('automation_run_id')

    # Start a new automation run
    new_run = api.automation_runs.create(
        package='package_id',
        name='automation_run_name',
        inputs={
            'x': 1,
            'y': 2,
            'z': 3
        }
    )

    # Stop an automation run
    new_run.stop()

    # Get automation run log
    state = run.log()

    # Get automation run state
    state = run.state()


Managing async operations
-------------------------

The following operations are supported for async operations runs:

    - ``list_file_jobs()`` - Query all async jobs for files.
    - ``get_copy_files_job()`` - Get the details of an asynchronous bulk file copy job.
    - ``get_delete_files_job()`` - Get the details of an asynchronous bulk file delete job.
    - ``get_file_move_job()`` - Get the details of an asynchronous bulk file move job.
    - ``get_result()`` - Parse results of a job as a bulk response.
    - ``file_bulk_copy()`` - Perform a bulk copy operation of files and folders. Any underlying folder structure will be preserved.
    - ``file_bulk_move()`` - Perform a bulk move operation of files and folders. Any underlying folder structure will be preserved.
    - ``file_bulk_delete()`` - Perform a bulk delete operation of files and folders. Deleting folders which aren't empty is allowed.

Properties
~~~~~~~~~~

Each async job has the following properties:

``id`` - Async job identifier.

``type`` - The type of job, which is COPY in the case of copying files, MOVE in case of moving files and DELETE in case of deleting files.

``state`` - Current job state (RUNNING, FINISHED, SUBMITTED, RESOLVING)

``result`` - The result of the copy job.

``total_files`` - The total number of files that were processed during the job.

``failed_files`` - The number of files that failed to copy.

``completed_files`` - The number of files that were successfully copied.

``started_on`` - The time and date the copy job started.

``finished_on`` - The time and date the copy job has finished.


Examples
~~~~~~~~

.. code:: python

    # Query all file jobs
    all_jobs = api.async_jobs.list_file_jobs().all()

    # Get file copy job by id
    copy_job = api.async_jobs.get_file_copy_job(id='copy_job_id')

    # Get file delete job by id
    delete_job = api.async_jobs.get_file_delete_job(id='delete_job_id')

    # Parse job results to bulk format
    copy_job_results = copy_job.get_result()

    # Check validity of each result in bulk format
    for result in copy_job_results:
        if result.valid:
            print(result.resource)
        else:
            print(result.error)

    # Start bulk file copy job
    files = [
        {
            'file': 'file_id_1',
            'parent': 'parent_id',
            'name': 'new_name_1',
        },
        {
            'file': 'file_id_2',
            'parent': 'parent_id',
            'name': 'new_name_2',
        },
    ]
    new_copy_job = api.async_jobs.file_bulk_copy(files=files)

    # Start bulk file delete job
    files = [
        {
            'file': 'file_id_1'
        },
        {
            'file': 'file_id_2'
        },
    ]
    new_delete_job = api.async_jobs.file_bulk_delete(files=files)

    # Start bulk file move job
        files = [
            {
                'file': 'file_id_1',
                'project': project_id,
                'name': 'name_1',
            },
            {
                'file': 'file_id_2',
                'project': project_id,
                'name': 'name_2',
            },
            {
                'file': 'file_id_3',
                'project': project_id,
                'name': 'name_2',
            }
        ]
        new_move_job = api.async_jobs.file_bulk_move(files=files)
