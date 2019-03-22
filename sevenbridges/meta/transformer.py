from datetime import datetime

import six

from sevenbridges.errors import SbgError


class Transform(object):
    @staticmethod
    def to_resource(resource):
        from sevenbridges.meta.resource import Resource
        if not resource:
            raise SbgError('Invalid id value!')
        elif isinstance(resource, Resource) and hasattr(resource, 'id'):
            return resource.id
        elif isinstance(resource, six.string_types):
            return resource
        else:
            raise SbgError('Invalid id value!')

    @staticmethod
    def to_project(project):
        """Serializes project to id string
        :param project: object to serialize
        :return: string id
        """
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
        """Serializes task to id string
        :param task: object to serialize
        :return: string id
        """
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
        """Serializes app to id string
        :param app: object to serialize
        :return: string id
        """
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
        """Serializes file to id string
        :param file_: object to serialize
        :return: string id
        """
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
        """Serializes user to id string
        :param user: object to serialize
        :return: string id
        """
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
        """Serializes billing_group to id string
        :param billing_group: object to serialize
        :return: string id
        """
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
        """Serializes volume to id string
        :param volume: object to serialize
        :return: string id
        """
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
    def to_marker(marker):
        """Serializes marker to string
        :param marker: object to serialize
        :return: string id
        """
        from sevenbridges.models.marker import Marker
        if not marker:
            raise SbgError('Marker is required!')
        elif isinstance(marker, Marker):
            return marker.id
        elif isinstance(marker, six.string_types):
            return marker
        else:
            raise SbgError('Invalid marker parameter!')

    @staticmethod
    def to_datestring(d):
        """Serializes date to string
        :param d: object to serialize
        :return: string date
        """
        if not d:
            raise SbgError('Date is required!')
        elif isinstance(d, six.string_types):
            return d
        elif isinstance(d, datetime):
            return d.isoformat().split('.', 1)[0]

    @staticmethod
    def to_division(division):
        """Serializes division to id string
        :param division: object to serialize
        :return: string id
        """
        from sevenbridges.models.division import Division
        if not division:
            raise SbgError('Division is required!')
        elif isinstance(division, Division):
            return division.id
        elif isinstance(division, six.string_types):
            return division
        else:
            raise SbgError('Invalid division parameter!')

    @staticmethod
    def to_team(team):
        """Serializes team to id string
        :param team: object to serialize
        :return: string id
        """
        from sevenbridges.models.team import Team
        if not team:
            raise SbgError('Team is required!')
        elif isinstance(team, Team):
            return team.id
        elif isinstance(team, six.string_types):
            return team
        else:
            raise SbgError('Invalid team parameter!')

    @staticmethod
    def to_import(import_):
        """Serializes import to id string
        :param import_: object to serialize
        :return: string id
        """
        from sevenbridges.models.storage_import import Import
        if not import_:
            raise SbgError('Import is required!')
        elif isinstance(import_, Import):
            return import_.id
        elif isinstance(import_, six.string_types):
            return import_
        else:
            raise SbgError('Invalid import parameter!')

    @staticmethod
    def to_export(export):
        """Serializes export to id string
        :param export: object to serialize
        :return: string id
        """
        from sevenbridges.models.storage_export import Export
        if not export:
            raise SbgError('Export is required!')
        elif isinstance(export, Export):
            return export.id
        elif isinstance(export, six.string_types):
            return export
        else:
            raise SbgError('Invalid export parameter!')

    @staticmethod
    def to_location(location):
        """Serializes location to string
        :param location: object to serialize
        :return: string
        """
        if not location:
            raise SbgError('Location is required!')
        if isinstance(location, six.string_types):
            return location
        else:
            raise SbgError('Invalid location parameter!')

    @staticmethod
    def to_dataset(dataset):
        from sevenbridges.models.dataset import Dataset
        if not dataset:
            raise SbgError('Dataset is required!')
        if isinstance(dataset, Dataset):
            return dataset.id
        if isinstance(dataset, six.string_types):
            return dataset
        else:
            raise SbgError('Invalid dataset parameter!')

    @staticmethod
    def to_member(member):
        from sevenbridges.models.member import Member
        if not member:
            raise SbgError('Member is required!')
        if isinstance(member, Member):
            return member.username
        if isinstance(member, six.string_types):
            return member
        else:
            raise SbgError('Invalid member parameter!')

    @staticmethod
    def to_automation(automation):
        from sevenbridges.models.automation import Automation
        if not automation:
            raise SbgError('Automation is required!')
        if isinstance(automation, Automation):
            return automation.id
        if isinstance(automation, six.string_types):
            return automation
        else:
            raise SbgError('Invalid automation parameter!')

    @staticmethod
    def to_automation_member(member):
        from sevenbridges.models.automation import AutomationMember
        if not member:
            raise SbgError('Automation member is required!')
        if isinstance(member, AutomationMember):
            return member.username
        if isinstance(member, six.string_types):
            return member
        else:
            raise SbgError('Invalid automation member parameter!')

    @staticmethod
    def to_automation_package(package):
        from sevenbridges.models.automation import AutomationPackage
        if not package:
            raise SbgError('Automation package is required!')
        if isinstance(package, AutomationPackage):
            return package.id
        if isinstance(package, six.string_types):
            return package
        else:
            raise SbgError('Invalid automation package parameter!')

    @staticmethod
    def to_async_job(async_job):
        from sevenbridges.models.async_jobs import AsyncJob
        if not async_job:
            raise SbgError('Async job is required!')
        if isinstance(async_job, AsyncJob):
            return async_job.id
        if isinstance(async_job, six.string_types):
            return async_job
        else:
            raise SbgError('Invalid async job parameter!')
