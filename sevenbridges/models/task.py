import logging
import six

from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import (
    SbgError, TaskValidationError
)
from sevenbridges.meta.fields import (
    HrefField, UuidField, StringField, CompoundField, DateTimeField,
    BooleanField, DictField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform
from sevenbridges.models.app import App
from sevenbridges.models.compound.price import Price
from sevenbridges.models.compound.tasks.batch_by import BatchBy
from sevenbridges.models.compound.tasks.batch_group import BatchGroup
from sevenbridges.models.compound.tasks.execution_status import ExecutionStatus
from sevenbridges.models.compound.tasks.input import Input
from sevenbridges.models.compound.tasks.output import Output
from sevenbridges.models.execution_details import ExecutionDetails
from sevenbridges.models.file import File

log = logging.getLogger(__name__)


class Task(Resource):
    """
    Central resource for managing tasks.
    """
    _URL = {
        'query': '/tasks',
        'get': '/tasks/{id}',
        'delete': '/tasks/{id}',
        'run': '/tasks/{id}/actions/run',
        'abort': '/tasks/{id}/actions/abort',
        'execution_details': "/tasks/{id}/execution_details"
    }

    href = HrefField()
    id = UuidField()
    name = StringField()
    status = StringField(read_only=True)
    description = StringField(read_only=False)
    project = StringField()
    app = StringField()
    type = StringField(read_only=True)
    created_by = StringField(read_only=True)
    executed_by = StringField(read_only=True)
    start_time = DateTimeField(read_only=True)
    batch = BooleanField(read_only=True)
    batch_by = CompoundField(BatchBy, read_only=False)
    batch_group = CompoundField(BatchGroup, read_only=True)
    batch_input = StringField(read_only=False)
    parent = StringField(read_only=True)
    end_time = DateTimeField(read_only=True)
    execution_status = CompoundField(ExecutionStatus, read_only=True)
    errors = DictField(read_only=True)
    warnings = DictField(read_only=True)
    price = CompoundField(Price, read_only=True)
    inputs = CompoundField(Input, read_only=False)
    outputs = CompoundField(Output, read_only=True)

    def __str__(self):
        return six.text_type('<Task: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, project=None, status=None, batch=None,
              parent=None, created_from=None, created_to=None,
              started_from=None, started_to=None, ended_from=None,
              ended_to=None, offset=None, limit=None, api=None):
        """
        Query (List) tasks. Date parameters may be both strings and python date
        objects.
        :param project: Target project. optional.
        :param status: Task status.
        :param batch: Only batch tasks.
        :param parent: Parent batch task identifier.
        :param ended_to: All tasks that ended until this date.
        :param ended_from: All tasks that ended from this date.
        :param started_to: All tasks that were started until this date.
        :param started_from: All tasks that were started from this date.
        :param created_to: All tasks that were created until this date.
        :param created_from: All tasks that were created from this date.
        :param offset: Pagination offset.
        :param limit: Pagination limit.
        :param api: Api instance.
        :return: Collection object.
        """
        api = api or cls._API
        if parent:
            parent = Transform.to_task(parent)
        if project:
            project = Transform.to_project(project)
        if created_from:
            created_from = Transform.to_datestring(created_from)
        if created_to:
            created_to = Transform.to_datestring(created_to)
        if started_from:
            started_from = Transform.to_datestring(started_from)
        if started_to:
            started_to = Transform.to_datestring(started_to)
        if ended_from:
            ended_from = Transform.to_datestring(ended_from)
        if ended_to:
            ended_to = Transform.to_datestring(ended_to)

        return super(Task, cls)._query(
            url=cls._URL['query'], project=project, status=status, batch=batch,
            parent=parent, created_from=created_from, created_to=created_to,
            started_from=started_from, started_to=started_to,
            ended_from=ended_from, ended_to=ended_to, offset=offset,
            limit=limit, fields='_all', api=api
        )

    @classmethod
    def create(cls, name, project, app, revision=None, batch_input=None,
               batch_by=None, inputs=None, description=None, run=False,
               disable_batch=False, api=None):

        """
        Creates a task on server.
        :param name: Task name.
        :param project: Project identifier.
        :param app: CWL app identifier.
        :param revision: CWL app revision.
        :param batch_input: Batch input.
        :param batch_by: Batch criteria.
        :param inputs: Input map.
        :param description: Task description.
        :param run: True if you want to run a task upon creation.
        :param disable_batch: If True disables batching of a batch task.
        :param api: Api instance.
        :return: Task object.
        :raises: TaskValidationError if validation Fails.
        :raises: SbgError if any exception occurs during request.
        """
        task_data = {}
        params = {}

        project = Transform.to_project(project)

        app_id = Transform.to_app(app)

        if revision:
            app_id = app_id + "/" + six.text_type(revision)
        else:
            if isinstance(app, App):
                app_id = app_id + "/" + six.text_type(app.revision)

        task_inputs = {'inputs': {}}
        for k, v in inputs.items():
            if isinstance(v, File):
                input = {
                    'class': 'File',
                    'path': v.id,
                }
                task_inputs['inputs'][k] = input
            elif isinstance(v, list):
                input_list = []
                for inp in v:
                    if isinstance(inp, File):
                        input = {
                            'class': 'File',
                            'path': inp.id,
                        }
                        if inp.name:
                            input['name'] = inp.name
                        input_list.append(input)

                    else:
                        input_list.append(inp)
                task_inputs['inputs'][k] = input_list
            else:
                task_inputs['inputs'][k] = v

        if batch_input and batch_by:
            task_data['batch_input'] = batch_input
            task_data['batch_by'] = batch_by
            if disable_batch:
                params.update({'batch': False})

        task_meta = {
            'name': name,
            'project': project,
            'app': app_id,
            'description': description
        }
        task_data.update(task_meta)
        task_data.update(task_inputs)

        if run:
            params.update({'action': 'run'})

        api = api if api else cls._API
        created_task = api.post(cls._URL['query'], data=task_data,
                                params=params).json()
        if run and 'errors' in created_task:
            if bool(created_task['errors']):
                raise TaskValidationError(
                    'Unable to run task! Task contains errors.',
                    task=Task(api=api, **created_task)
                )

        return Task(api=api, **created_task)

    @classmethod
    def smart_create(cls, name, project, app, revision=None, batch_input=None,
                     batch_by=None,
                     file_inputs=None, app_settings=None, description=None, run=False, api=None):
        """
        Creates a task on server. Takes file names for file_input values and smartly retrieves
        the file objects from the project. Calls 'create' internally
        :param name: Task name.
        :param project: Project identifier.
        :param app: CWL app identifier.
        :param revision: CWL app revision.
        :param batch_input: Batch input.
        :param batch_by: Batch criteria.
        :param file_inputs: Input map with file names.
        :param app_settings: Input map with app settings (not file objects)
        :param description: Task description.
        :param run: True if you want to run a task upon creation.
        :param api: Api instance.
        :return: Task object.
        """
        inputs = app_settings or {}
        inputs.update(**cls.fileify(api if api else cls._API, project, file_inputs))
        cls.create(name, project, app, revision=revision, batch_input=batch_input, batch_by=batch_by,
                   inputs=inputs, description=description, run=run, api=api)

    @staticmethod
    def fileify(api, project, file_inputs):
        """Given a dictionary representing file inputs retrieve the file objects for all of them"""

        # Get a dict mapping file name -> file object(s) from the project
        fl = {f.name: f for f in api.files.query(
            project=project,
            names=[v for f in file_inputs.values() for v in (lambda x: x if isinstance(x, list) else [x])(f)])}

        # Replace the file_inputs dictionary string values with file objects
        return {
            k: [fl[ff] for ff in v] if isinstance(v, list) else fl[v] for k, v in file_inputs.items()
        }

    @inplace_reload
    def abort(self, inplace=True):
        """
        Abort task
        :param inplace Apply action on the current object or return a new one.
        :return: Task object.
        """
        extra = {
            'resource': self.__class__.__name__,
            'query': {'id': self.id}
        }
        log.info('abort task', extra=extra)
        task_data = self._api.post(
            url=self._URL['abort'].format(id=self.id)).json()
        return Task(api=self._api, **task_data)

    @inplace_reload
    def run(self, batch=True, inplace=True):
        """
        Run task
        :param batch if False batching will be disabled.
        :param inplace Apply action on the current object or return a new one.
        :return: Task object.
        """
        params = {}
        if not batch:
            params['batch'] = False
        extra = {
            'resource': self.__class__.__name__,
            'query': {'id': self.id, 'batch': batch}
        }
        log.info('run task', extra=extra)
        task_data = self._api.post(
            url=self._URL['run'].format(id=self.id), params=params).json()
        return Task(api=self._api, **task_data)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the task on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Task instance.
        """
        modified_data = self._modified_data()
        if bool(modified_data):
            task_request_data = {}
            inputs = modified_data.pop('inputs', None)
            task_request_data.update(modified_data)
            if inputs:
                task_request_data['inputs'] = {}
                for input_id, input_value in inputs.items():
                    if isinstance(input_value, File):
                        in_file = Task._to_api_file_format(input_value)
                        task_request_data['inputs'][input_id] = in_file
                    elif isinstance(input_value, list):
                        in_list = [item for item in input_value if
                                   not isinstance(item, File)]
                        in_list.extend([Task._to_api_file_format(item)
                                        for item in input_value if
                                        isinstance(item, File)])

                        task_request_data['inputs'][input_id] = in_list
                    else:
                        task_request_data['inputs'][input_id] = input_value
            extra = {
                'resource': self.__class__.__name__,
                'query': {'id': self.id, 'data': task_request_data}
            }
            log.info('save task', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=task_request_data).json()
            task = Task(api=self._api, **data)
            return task

    @staticmethod
    def _to_api_file_format(_file):
        api_file = {'class': 'File', 'path': _file.id}
        if _file.name:
            api_file['name'] = _file.name
        return api_file

    def get_execution_details(self):
        """
        Retrieves execution details for a task.
        :return: Execution details instance.
        """
        extra = {
            'resource': self.__class__.__name__,
            'query': {'id': self.id}
        }
        log.info('get execution details', extra=extra)
        data = self._api.get(
            self._URL['execution_details'].format(id=self.id)).json()
        return ExecutionDetails(api=self._api, **data)

    def get_batch_children(self):
        """
        Retrieves batch child tasks for this task if its a batch task.
        :return: Collection instance.
        :raises SbError if task is not a batch task.
        """
        if not self.batch:
            raise SbgError("This task is not a batch task.")
        return self.query(parent=self.id, api=self._api)
