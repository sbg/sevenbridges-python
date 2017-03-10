from datetime import datetime

import six
from sevenbridges.errors import SbgError


class Transform(object):
    @staticmethod
    def to_project(project):
        from sevenbridges.models.project import Project
        if not project:
            raise SbgError('Project is required!')
        elif isinstance(project, Project):
            return project.id
        elif isinstance(project, six.string_types):
            return project
        else:
            raise SbgError('Invalid project parameter!')

    @staticmethod
    def to_task(task):
        from sevenbridges.models.task import Task
        if not task:
            raise SbgError('Task is required!')
        elif isinstance(task, Task):
            return task.id
        elif isinstance(task, six.string_types):
            return task
        else:
            raise SbgError('Invalid task parameter!')

    @staticmethod
    def to_app(app):
        from sevenbridges.models.app import App
        if not app:
            raise SbgError('App is required!')
        elif isinstance(app, App):
            return app.id
        elif isinstance(app, six.string_types):
            return app
        else:
            raise SbgError('Invalid app parameter!')

    @staticmethod
    def to_file(file_):
        from sevenbridges.models.file import File
        if not file_:
            raise SbgError('File is required!')
        elif isinstance(file_, File):
            return file_.id
        elif isinstance(file_, six.string_types):
            return file_
        else:
            raise SbgError('Invalid file parameter!')

    @staticmethod
    def to_user(user):
        from sevenbridges.models.user import User
        if not user:
            raise SbgError('User is required!')
        elif isinstance(user, User):
            return user.username
        elif isinstance(user, six.string_types):
            return user
        else:
            raise SbgError('Invalid user parameter!')

    @staticmethod
    def to_billing_group(billing_group):
        from sevenbridges.models.billing_group import BillingGroup
        if not billing_group:
            raise SbgError('Billing group is required!')
        elif isinstance(billing_group, BillingGroup):
            return billing_group.id
        elif isinstance(billing_group, six.string_types):
            return billing_group
        else:
            raise SbgError('Invalid billing group parameter!')

    @staticmethod
    def to_volume(volume):
        from sevenbridges.models.volume import Volume
        if not volume:
            raise SbgError('Volume is required!')
        elif isinstance(volume, Volume):
            return volume.id
        elif isinstance(volume, six.string_types):
            return volume
        else:
            raise SbgError('Invalid volume parameter!')

    @staticmethod
    def to_datestring(d):
        if not d:
            raise SbgError('Date is required!')
        elif isinstance(d, six.string_types):
            return d
        elif isinstance(d, datetime):
            return d.isoformat().split('.', 1)[0]
