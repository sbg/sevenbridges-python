import time
import logging

from sevenbridges.models.bulk import BulkRecord
from sevenbridges.decorators import inplace_reload
from sevenbridges.errors import (
    SbgError, TaskValidationError
)

from sevenbridges.meta.fields import (
    HrefField, UuidField, StringField,
    CompoundField, DateTimeField,
    BooleanField, DictField
)
from sevenbridges.meta.resource import Resource
from sevenbridges.meta.transformer import Transform

from sevenbridges.models.app import App
from sevenbridges.models.file import File
from sevenbridges.models.enums import FileApiFormats, TaskStatus
from sevenbridges.models.compound.price import Price
from sevenbridges.models.compound.tasks.batch_by import BatchBy
from sevenbridges.models.compound.tasks.batch_group import BatchGroup
from sevenbridges.models.compound.tasks.execution_status import ExecutionStatus
from sevenbridges.models.compound.tasks.input import Input
from sevenbridges.models.compound.tasks.output import Output
from sevenbridges.models.execution_details import ExecutionDetails

logger = logging.getLogger(__name__)


class Task(Resource):
    """
    Central resource for managing tasks.
    """
    _URL = {
        'query': '/tasks',
        'get': '/tasks/{id}',
        'delete': '/tasks/{id}',
        'run': '/tasks/{id}/actions/run',
        'clone': '/tasks/{id}/actions/clone',
        'abort': '/tasks/{id}/actions/abort',
        'execution_details': "/tasks/{id}/execution_details",
        'bulk_get': '/bulk/tasks/get',
    }

    href = HrefField(read_only=True)
    id = UuidField(read_only=True)
    name = StringField(read_only=False)
    status = StringField(read_only=True)
    description = StringField(read_only=False)
    project = StringField(read_only=False)
    app = StringField(read_only=False)
    type = StringField(read_only=True)
    created_by = StringField(read_only=True)
    executed_by = StringField(read_only=True)
    start_time = DateTimeField(read_only=True)
    created_time = DateTimeField(read_only=True)
    end_time = DateTimeField(read_only=True)
    batch = BooleanField(read_only=False)
    batch_by = CompoundField(BatchBy, read_only=False)
    batch_group = CompoundField(BatchGroup, read_only=True)
    batch_input = StringField(read_only=False)
    parent = StringField(read_only=True)
    execution_status = CompoundField(ExecutionStatus, read_only=True)
    errors = DictField(read_only=True)
    warnings = DictField(read_only=True)
    price = CompoundField(Price, read_only=True)
    inputs = CompoundField(Input, read_only=False)
    outputs = CompoundField(Output, read_only=True)
    execution_settings = DictField(read_only=True)
    output_location = DictField(read_only=True)
    use_interruptible_instances = BooleanField(read_only=False)
    origin = StringField(read_only=True, name='origin_id')

    def __str__(self):
        return f'<Task: id={self.id}>'

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return self is other or self.id == other.id

    @classmethod
    def query(cls, project=None, status=None, batch=None,
              parent=None, created_from=None, created_to=None,
              started_from=None, started_to=None, ended_from=None,
              ended_to=None, offset=None, limit=None, order_by=None,
              order=None, origin=None, api=None):
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
        :param order_by: Property to order by.
        :param order: Ascending or descending ordering.
        :param origin: Entity that created the task, e.g. automation run,
        if task was created by an automation run.
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
        if origin:
            origin = Transform.to_automation_run(origin)

        return super()._query(
            url=cls._URL['query'], project=project, status=status, batch=batch,
            parent=parent, created_from=created_from, created_to=created_to,
            started_from=started_from, started_to=started_to,
            ended_from=ended_from, ended_to=ended_to, offset=offset,
            limit=limit, order_by=order_by, order=order, fields='_all',
            origin_id=origin, api=api
        )

    @classmethod
    def create(cls, name, project, app, revision=None, batch_input=None,
               batch_by=None, inputs=None, description=None, run=False,
               disable_batch=False, interruptible=None,
               execution_settings=None, output_location=None, api=None):

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
        :param interruptible: If True interruptible instance will be used.
        :param execution_settings: Execution settings for the task.
        :param output_location: Dictionary that allows you to define the exact
        location where your task outputs will be stored.
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
            app_id = f'{app_id}/{revision}'
        else:
            if isinstance(app, App):
                app_id = f'{app_id}/{app.revision}'

        task_inputs = {
            'inputs': Task._serialize_inputs(inputs) if inputs else {}
        }

        if batch_input and batch_by:
            task_data['batch_input'] = batch_input
            task_data['batch_by'] = batch_by
            if disable_batch:
                params.update({'batch': False})

        task_meta = {
            'name': name,
            'project': project,
            'app': app_id,
            'description': description,
        }
        task_data.update(task_meta)
        task_data.update(task_inputs)

        if interruptible is not None:
            task_data['use_interruptible_instances'] = interruptible

        if execution_settings:
            task_data.update({'execution_settings': execution_settings})

        if output_location:
            task_data.update({'output_location': output_location})

        if run:
            params.update({'action': 'run'})

        api = api if api else cls._API
        created_task = api.post(cls._URL['query'], data=task_data,
                                params=params).json()
        if run and 'errors' in created_task and created_task['errors']:
            raise TaskValidationError(
                'Unable to run task! Task contains errors.',
                task=Task(api=api, **created_task)
            )

        return Task(api=api, **created_task)

    @inplace_reload
    def abort(self, inplace=True):
        """
        Abort task
        :param inplace Apply action on the current object or return a new one.
        :return: Task object.
        """
        extra = {
            'resource': type(self).__name__,
            'query': {'id': self.id}
        }
        logger.info('Aborting task', extra=extra)
        task_data = self._api.post(
            url=self._URL['abort'].format(id=self.id)).json()
        return Task(api=self._api, **task_data)

    @inplace_reload
    def run(self, batch=True, interruptible=None, inplace=True):
        """
        Run task
        :param batch if False batching will be disabled.
        :param interruptible: If true interruptible instance
        will be used.
        :param inplace Apply action on the current object or return a new one.
        :return: Task object.
        """
        params = {}
        if not batch:
            params['batch'] = False
        if interruptible is not None:
            params['use_interruptible_instances'] = interruptible
        extra = {
            'resource': type(self).__name__,
            'query': {'id': self.id, 'batch': batch}
        }
        logger.info('Running task', extra=extra)
        task_data = self._api.post(
            url=self._URL['run'].format(id=self.id), params=params).json()
        return Task(api=self._api, **task_data)

    def clone(self, run=True):
        """
        Clone task
        :param run: run task after cloning
        :return: Task object.
        """
        params = {}
        if run:
            params.update({'action': 'run'})

        extra = {
            'resource': type(self).__name__,
            'query': {'id': self.id, 'run': run}
        }
        logger.info('Cloning task', extra=extra)
        task_data = self._api.post(
            url=self._URL['clone'].format(id=self.id), params=params).json()

        return Task(api=self._api, **task_data)

    @inplace_reload
    def save(self, inplace=True):
        """
        Saves all modification to the task on the server.
        :param inplace Apply edits on the current instance or get a new one.
        :return: Task instance.
        """
        modified_data = self._modified_data()
        if modified_data:
            task_request_data = {}
            inputs = modified_data.pop('inputs', None)
            execution_settings = modified_data.pop('execution_settings', None)
            task_request_data.update(modified_data)

            if inputs:
                task_request_data['inputs'] = self._serialize_inputs(inputs)

            if execution_settings:
                task_request_data['execution_settings'] = (
                    self._serialize_execution_settings(execution_settings)
                )

            extra = {
                'resource': type(self).__name__,
                'query': {'id': self.id, 'data': task_request_data}
            }
            logger.info('Saving task', extra=extra)
            data = self._api.patch(url=self._URL['get'].format(id=self.id),
                                   data=task_request_data).json()
            task = Task(api=self._api, **data)
            return task

    def _serialize_execution_settings(self, execution_settings):
        instance_type = execution_settings.get(
            'instance_type',
            self.execution_settings.get('instance_type', None)
        )
        max_parallel_instances = execution_settings.get(
            'max_parallel_instances',
            self.execution_settings.get('max_parallel_instances', None)
        )
        use_memoization = execution_settings.get(
            'use_memoization',
            self.execution_settings.get('use_memoization', None)
        )
        use_elastic_disc = execution_settings.get(
            'use_elastic_disc',
            self.execution_settings.get('use_elastic_disc', None)
        )
        serialized_es_mapping = {
            'instance_type': instance_type,
            'max_parallel_instances': max_parallel_instances,
            'use_memoization': use_memoization,
            'use_elastic_disc': use_elastic_disc
        }
        serialized_es = dict()
        for key, value in serialized_es_mapping.items():
            if value is not None:
                serialized_es[key] = value

        return serialized_es

    @staticmethod
    def _serialize_inputs(input_value):
        """
        Recursively serialises input dictionary.
        :param input_value: input dictionary to serialize
        :return: serialized input dictionary
        """
        if isinstance(input_value, list):
            return_value = []
            for elem in input_value:
                return_value.append(Task._serialize_inputs(elem))
        elif isinstance(input_value, dict):
            return_value = {}
            for key in input_value:
                return_value[key] = Task._serialize_inputs(
                    input_value[key]
                )
        elif isinstance(input_value, File):
            return_value = Task._to_api_file_format(input_value)
        else:
            return_value = input_value
        return return_value

    @staticmethod
    def _to_api_file_format(_file):
        return {
            'class': (
                FileApiFormats.FOLDER if _file.is_folder()
                else FileApiFormats.FILE
            ),
            'path': _file.id
        }

    def get_execution_details(self):
        """
        Retrieves execution details for a task.
        :return: Execution details instance.
        """
        extra = {
            'resource': type(self).__name__,
            'query': {'id': self.id}
        }
        logger.info('Get execution details', extra=extra)
        data = self._api.get(
            self._URL['execution_details'].format(id=self.id)).json()
        return ExecutionDetails(api=self._api, **data)

    def get_batch_children(self, status=None, created_from=None,
                           created_to=None, started_from=None, started_to=None,
                           ended_from=None, ended_to=None, order_by=None,
                           order=None, offset=None, limit=None, api=None):
        """
        Retrieves batch child tasks for this task if its a batch task.
        :return: Collection instance.
        :raises SbError if task is not a batch task.
        """
        api = api or self._api
        if not self.batch:
            raise SbgError("This task is not a batch task.")
        return self.query(
            parent=self.id, status=status, created_from=created_from,
            created_to=created_to, started_from=started_from,
            started_to=started_to, ended_from=ended_from, ended_to=ended_to,
            order_by=order_by, order=order, offset=offset, limit=limit,
            api=api,
        )

    @classmethod
    def bulk_get(cls, tasks, api=None):
        """
        Retrieve tasks with specified ids in bulk
        :param tasks: Tasks to be retrieved.
        :param api: Api instance.
        :return: List of TaskBulkRecord objects.
        """
        api = api or cls._API
        task_ids = [Transform.to_task(task) for task in tasks]
        data = {'task_ids': task_ids}

        logger.debug('Getting tasks in bulk.')
        response = api.post(url=cls._URL['bulk_get'], data=data)
        return TaskBulkRecord.parse_records(response=response, api=api)

    def wait(self=None, period=10, callback=None, *args, **kwargs):
        """Wait until task is complete
        :param period: Time in seconds between reloads
        :param callback: Function to call after the task has finished,
            arguments and keyword arguments can be provided for it
        :return: Return value of provided callback function or None if a
            callback function was not provided
        """
        while self.status not in TaskStatus.terminal_states:
            self.reload()
            time.sleep(period)

        if callback:
            return callback(*args, **kwargs)


class TaskBulkRecord(BulkRecord):
    resource = CompoundField(cls=Task, read_only=False)

    def __str__(self):
        return f'<TaskBulkRecord valid={self.valid}>'
