
Quickstart
==========

Authentication and Configuration
--------------------------------

--------------

In order to authenticate to the API, sevenbridges-python library
requires that you pass in your authentication token and URL endpoint,
acquired from the Seven Bridges Platform or Seven Bridges related
products like Cancer Genomics Cloud.

You can find your authentication token on the respective platform pages:

-  https://igor.sbgenomics.com/developers
-  https://cgc.sbgenomics.com/developers

Apart from this, you need to define the API endpoint, which is:

-  https://api.sbgenomics.com/v2 for Seven Bridges Platform
-  https://cgc-api.sbgenomics.com/v2 for the CGC.

The api documentation is available:

-  http://docs.sevenbridges.com/docs/the-api for Seven Bridges Platform.
-  http://docs.cancergenomicscloud.org/docs/the-cgc-api for the CGC.

Initializing the library
~~~~~~~~~~~~~~~~~~~~~~~~

Once you obtain your authentication token you can pass it to the Config
object. You can instantiate your Api object by passing the appropriate
configuration. There are three ways you can configure the library:

1. Pass parameters ``url`` and ``token`` explicitly when initializing
   api object.
2. Put API endpoint and token in the environment variables ``API_URL``
   and ``AUTH_TOKEN`` respectively.
3. Use configuration file ``$HOME/.sbgrc`` with defined parameters.

*Note on authentication information*:

Keep your authentication token safe, as you would keep any other secret
information. Generally, we recommend using configuration file, as the
authentication token is then stored on user's home folder and no strewn
about in code and committed to source code repositories.

Import the library
~~~~~~~~~~~~~~~~~~

.. code:: python

    import sevenbridges as sbg

Initialize the library using configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Api object represents the central resource for querying, saving and
performing all sort of actions on your resources. Once you have
instantiated configuration class, pass it to the API class constructor.

.. code:: python

    c = sbg.Config(profile='sbpla')
    api = sbg.Api(config=c)

Initialize the library using environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import os
    
    # Usually these would be set in the shell beforehand
    os.environ['API_URL'] = 'https://api.sbgenomics.com/v2'
    os.environ['AUTH_TOKEN'] = '<TOKEN_HERE>'
    
    c = sbg.Config()
    api = sbg.Api(config=c)

Initialize library explicitly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Library can be also instatiated explicity by passing the url and token
as key value arguments.

.. code:: python

    api = sbg.Api(url='https://api.sbgenomics.com/v2', token='27d598b71beb4660952739ed5f94ebda')

*Note* - you can always initialize several API clients with possibly
different credentials or talking to a different environment

Notes on config file format
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Format of the ``.sbgrc`` file is as a simple .ini file format, with
profile shown in brackets.

::

    [sbpla]
    api-url = 'https://api.sbgenomics.com/v2'
    auth-token = 700992f7b24a470bb0b028fe813b8100

    [cgc]
    api-url = 'https://api.sbgenomics.com/v2'
    auth-token = 910975f5b24a470bb0b028fe813b8100

Rate limit
----------

--------------

For requests using authentication, you can issue a maximum of 1000
requests per 300 seconds. Note that this limit is generally subject to
change, depending on API usage and technical limits. Your current rate
limit, the number of remaining request, or the rate reset time can be
obtained using your Api object.

.. code:: python

    api.limit, api.remaining, api.reset_time

Managing users
--------------

--------------

Currently authenticated user can always access his/her's information by
invoking the following method.

.. code:: python

    me = api.users.me()

**me** object now contains user information including:

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

For example to obtain your email invoke:

.. code:: python

    me.email

Managing projects
-----------------

--------------

There are several methods on the Api object which can help you manage
your projects.

In order to list or query projects invoke a query method. Query method
follows server pagination and therefore initial pagination parameters
can be passed to the query method. **offset** parameter controls the
start of the pagination while the **limit** parameter controls the
number of items you want to be retrieved.

.. code:: python

    project_list = api.projects.query(offset=0, limit=10)

**project\_list** is now an object of the type **Collection** which acts
just like a regular python list. What that means is that is supports
indexing, slicing, iterating and other list functions. All collections
in the python-sbg library have two methods **next\_page** and
**previous\_page** which allow you to load next pagination page or
previous pagination page.

List Projects - introduction to paging and iteration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are several things you can do with a collection of any kind of
objects:

1. The generic query, like ``api.projects.query()`` accepts offset and
   limit parameters.
2. If you wish to iterate on complete collection use ``all()`` method,
   which returns an iterator
3. If you have a need to manually iterate on the collection (page per
   page), use ``next_page()`` and ``previous_page()`` methods on the
   collection.
4. You can easily cast the collection to the list, so you can re-use it
   later by issuing Python standard
   ``project_list = list(api.projects.query().all())``.

.. code:: python

    # Query first 10 projects.
    project_list = api.projects.query(limit=10)

.. code:: python

    # Iterate on all projects and print out name and id
    for project in api.projects.query().all():
        print (project.id,project.name)

.. code:: python

    # Get all my current projects and store them in a list
    my_projects = list(api.projects.query().all())

Get single project
~~~~~~~~~~~~~~~~~~

You can get a single project by issuing ``api.projects.get()`` method
with a parameter ``id``, signifying the id of a project. Note that this
call, as well as other calls to the API server will raise an Exception
which you can catch and process if required.

.. code:: python

    from sevenbridges.errors import SbgError
    try:
        project_id = 'doesnotexist/forsure'
        project = api.projects.get(id=project_id)
    except SbgError as e:
        print (e.message)

*Note* - when you wish to process errors from the library, you need to
import errors from ``sevenbridges.errors``.

Most often you will use ``SbgError``, as this error has properties
``code`` and ``message`` which relate to API status codes:

-  http://docs.sevenbridges.com/docs/api-status-codes for Seven Bridges
   Platform

-  http://docs.cancergenomicscloud.org/docs/api-status-codes for the
   CGC.

Project properties
~~~~~~~~~~~~~~~~~~

Once you have your Project instance it has the following properties
attached:

::

    project.href - project href on the API 
    project.id - id of the project
    project.name - name of the project
    project.description - description of the project
    project.billing_group - billing group attached to the project
    project.type - type of the project (v1 or v2)
    project.tags - list of project tags

**href** property is a url on the server that uniquely identifies the
resource. All resources will have this property attached. Project also
has its name, identifier, description its type and tags and also a
billing\_group identifier representing the billing group that is
attached to the project.

About methods
~~~~~~~~~~~~~

There are two types of methods in sevenbridges-python library, static
and dynamic. Static methods are invoked on the API object instance and
dynamic from the instance of the object representing the resource.

Static methods are:

1. Create a new resource -
   ``api.projects.create(name="My new project", billing_group='296a98a9-424c-43f3-aec5-306e0e41c799')``
   - creates a new resource. The parameters depend on the resource in
   question
2. Get resource - ``api.projects.get(id='user/project')`` - returns a
   specific resource, denoted by the id
3. Query resources - ``api.projects.query()`` method returns a pageable
   list of type ``Collection``. The same goes for other resources, so
   ``api.tasks.query(status='COMPLETED')`` returns a Collection of
   completed tasks with applied default paging.

Dynamic methods can be generic (for all resources) and specific. They
are called on the concrete object, like a ``Project`` object.

So if we have ``project`` variable as a ``Project`` object:

1. Delete resource - ``project.delete()`` - deletes object (if supported
   on the API).
2. Reload resource from server - ``project.reload()`` - reloads state of
   the object from the server.
3. Save changes to server - ``project.save()`` - saves all properties
   modified on the library

Project methods
~~~~~~~~~~~~~~~

The following example shows some manipulation of projects.

.. code:: python

    # Get a collection of projects
    projects = api.projects.query()
    
    # Grab first billing group 
    bg = api.billing_groups.query(limit=1)[0]
    
    # Create a project using the billing group 
    new_project = api.projects.create(name="My new project", billing_group=bg.id)
    
    # Add a new member to the project
    new_project.add_member(user='newuser', permissions= {'write':True, 'execute':True})

Other project methods include:

1. Get members of the project and their permissions -
   ``project.get_members()`` - returns a ``Collection`` of members and
   their permissions
2. Add member to the project - ``project.add_member()``
3. Remove member from the project - ``project.remove_member()``
4. List files from the project - ``project.get_files()``
5. Add files to the project - ``project.add_files`` - you can add a
   single ``File`` or a ``Collection`` of files
6. List apps from the project - ``project.get_apps()``
7. List tasks from the project - ``project.get_tasks``

Manage billing
--------------

--------------

There are several methods on the Api object which can help you manage
your billing information. The billing interface is separated to managing
*billing groups* and *invoices*.

Manage billing groups
~~~~~~~~~~~~~~~~~~~~~

Querying billing groups will return a standard collection object.

.. code:: python

    # Query billing groups
    bgroup_list = api.billing_groups.query(offset=0, limit=10)

.. code:: python

    # Fetching billing group information
    bg = api.billing_groups.get(id='f1969c90-da54-4118-8e96-c3f0b49a163d')

Billing group properties
~~~~~~~~~~~~~~~~~~~~~~~~

The following are properties that are attached to each billing group.

``href`` - Billing group href on the API server.

``id`` - Billing group identifier.

``owner`` - Username of the user that owns the billing group.

``name`` - Billing group name.

``type`` - Billing group type (free or regular)

``pending`` - True if billing group is not yet approved, False if
opposite is true.

``diabled`` - True if billing group is disabled, False if its enabled.

``balance`` - Billing group balance.

Billing group methods
~~~~~~~~~~~~~~~~~~~~~

``breakdown()`` - Fetches billing group breakdwon for this billing
groups that contains costs breakdown by projects and analysis.

Manage invoices
~~~~~~~~~~~~~~~

Querying invoices will return a Invoices collection object.

.. code:: python

    invoices = api.invoices.query()

Once you have obtain the invoice identifier you can also fetch specific
invoice information.

.. code:: python

    invoices = api.invoices.get(id='6351830069')

Invoice properties
~~~~~~~~~~~~~~~~~~

The following are properties that are attached to each billing group.

``href`` - Invoice href on the API server.

``id`` - Invoice identifier.

``pending`` - ``True`` if invoice is not yet approved, ``False`` if
invoice is approved.

``analysis_costs`` - Costs of your analysis.

``storage_costs`` - Storage costs.

``total`` - Total costs.

``invoice_period`` - Invoicing period (from-to)

Managing files
--------------

--------------

Files are integral part of each analysis. And as all other resources
with sevenbridges-python library user is able to efectivly query files,
get the specific file information and metadata. It can be achived in the
same manner as it was presented in projects and billing. Available
methods for fetching specific files is either ``query`` or a ``get``
method.

.. code:: python

    # Querying files
    file_list = api.files.query(project='user/my-project')

.. code:: python

    # Getting single file information
    file = api.files.get(id='5710141760b2b14e3cc146af')

File properties
~~~~~~~~~~~~~~~

Each of the files has the following properties attached:

``href`` - File href on the API server.

``id`` - File identifier.

``name`` - File name.

``size`` - File size in bytes.

``project`` - Identifier of the project that file is located in.

``created_on`` - Date of the file creation.

``modified_on`` - Last modification of the file.

``origin`` - File origin information.

``metadata`` - File metadata

File methods
~~~~~~~~~~~~

-  Refresh file with data from the server. ``reload()``
-  Copy file from one to another project. ``copy()``
-  Download file. ``download()``
-  Save modifications to the server ``save()``

Examples
~~~~~~~~

.. code:: python

    # Filter files per name containing certain string
    files = api.files.query(project='user/my-project')
    my_file = [file for file in files if 'fasta' in file.name]
    
    # Or simply query files by name if you know the exact name
    files = api.files.query(project='user/myproject', name='SRR062634.filt.fastq.gz')
    my_files = api.files.query(project='user/myproject', metadata = {'sample_id': 'SRR062634'} )
    
    
    # Edit metadata
    my_file = my_files[0]
    my_file['sample_id'] = 'my-sample'
    my_file['library'] = 'my-library'
    
    # Add metadata (if you are starting with a file without metadata)
    my_file = my_files[0]
    my_file.metadata = {'sample_id' : 'my-sample',
                        'library' : 'my-library'
                      }

    # Save modifications
    my_file.save()
    
    # Copy file
    new_file = my_file.copy(project='user/my-other-project', name='my-new-file')
    
    # Download file - by default it downloads the file with the same name to the current working directory
    new_file.download(wait=True)

Managing apps
-------------

--------------

Managing apps with sevenbridges-python library is simple. Apps on Seven
Bridges Platform and CGC are implemented using Common Workflow Language
specification
https://github.com/common-workflow-language/common-workflow-language.
The sevenbridges-python currenty supports only Draft 2 format of the
CWL.

Querying apps or getting a single app resource is available in the same
way as on other resources, using ``query()`` and ``get`` methods. You
can also invoke the following class methods:

-  'get\_revision()' - Returns specific app revision.
-  'install\_app()' - Installs you CWL app on the server.
-  'create\_revision()' - Creates a new revision from the specific app.

App properties
~~~~~~~~~~~~~~

The following is the list of available app properties.

``href`` - App href on the API server.

``id`` - App identifier.

``name`` - App name.

``project`` - Identifier of the project that app is located in.

``revision`` - App revision.

``raw`` - raw CWL format of the app.

App methods
~~~~~~~~~~~

Currently there is only one instance method and that is ``save()`` which
saves the app changes on the server.

Managing tasks
--------------

--------------

Tasks are easy to handle using sevenbridges-python library. As with all
resources you can ``query()`` your tasks, ``get()`` a single task
instance, but also do much more. We will outline task properties and
methods and show in the examples how easy is to run your first analysis.

Task properties
~~~~~~~~~~~~~~~

``href`` - Task href on the API server.

``id`` - Task identifier.

``name`` - Task name.

``status`` - Task status.

``project`` - Identifier of the project that task is located in.

``app`` - The app identifier that was used for this analysis.

``type`` - Task type.

``created_by`` - Username of task creator.

``executed_by``- Username of the task executor.

``batch`` - Boolean flag. True for batch tasks, False for regular &
child tasks.

``batch_by`` - Batching criteria.

``batch_group`` - Batch group assigned to the child task calculated from
the ``batch_by`` criteria.

``batch_input`` - Input identifier on to wich to apply batching.

``parent`` - Parent task for a batch child.

``end_time`` - Task end time.

``execution_status`` - Task execution status.

``price`` - Analysis cost.

``inputs`` - Inputs that were subbmited to the task.

``outputs`` - Generated outputs from the analysis.

Task methods
~~~~~~~~~~~~

The following represents the list of available class and instance
methods.

-  Create a task on the server and run it optionaly - ``create()``.
-  Query tasks - ``query()``.
-  Get single task information - ``get()``.
-  Abort a running task - ``abort()``.
-  Run a draft task. - ``run()``
-  Delete a draft task from the server. - ``delete()``.
-  Refresh the task object information with the date from the server. -
   ``refresh()``.
-  Save task modifications to the sever. - ``save()``.
-  Get task exection datails. - ``get_execution_details()``.
-  Get batch children if task is a batch task. -
   ``get_batch_children()``.

Task Examples
~~~~~~~~~~~~~

Single task
~~~~~~~~~~~

.. code:: python

    # Task name
    task_name = 'my-first-task'
    
    # Project in which I want to run a task.
    project_id = 'my-username/my-project'
    
    # App I want to use to run a task
    app = 'my-username/my-project/my-app'
    
    # Inputs
    inputs = {}
    inputs = {'FastQC-Reads'} = api.files.query(project='my-project', metadata={'sample': 'some-sample'})
    
    try:
        task = api.tasks.create(name=name, project=project, app=app, inputs=inputs, run=True)
    except SbError:
        print('I was unable to run the task.')
    
    # Task can also be ran by invoking .run() method on the draft task.
    task.run()

Batch task
~~~~~~~~~~

.. code:: python

    # Task name
    task_name = 'my-first-task'
    
    # Project in which I want to run a task.
    project_id = 'my-username/my-project'
    
    # App I want to use to run a task
    app = 'my-username/my-project/my-app'
    
    # Inputs
    inputs = {}
    inputs = {'FastQC-Reads'} = api.files.query(project='my-project', metadata={'sample': 'some-sample'})
    
    # Specifying that task should be created on per file basis.
    bach_by = {'type': 'item'}
    
    
    # Batch input is going to be FastQC-Reads
    batch_input = 'FastQC-Reads'
    
    try:
        task = api.tasks.create(name=name, project=project, app=app, 
                                inputs=inputs, batch_input=batch_input, batch_by=batch_by run=True)
    except SbError:
        print('I was unable to run a batch task.')
