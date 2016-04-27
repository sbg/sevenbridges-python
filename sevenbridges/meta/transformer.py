from sevenbridges.errors import SbgError


class Transform(object):
    @staticmethod
    def to_project(project):
        from sevenbridges.models.project import Project
        if project is None:
            raise SbgError('Project is required!')
        return project.id if isinstance(project, Project) else project

    @staticmethod
    def to_task(task):
        from sevenbridges.models.task import Task
        if task is None:
            raise SbgError('Task is required!')
        return task.id if isinstance(task, Task) else task

    @staticmethod
    def to_app(app):
        from sevenbridges.models.app import App
        if app is None:
            raise SbgError('App is required!')
        return app.id if isinstance(app, App) else app

    @staticmethod
    def to_file(file_):
        if file_ is None:
            raise SbgError('File is required!')
        from sevenbridges.models.file import File
        return file_.id if isinstance(file_, File) else file_

    @staticmethod
    def to_user(user):
        if user is None:
            raise SbgError('User is required!')
        from sevenbridges.models.user import User
        return user.username if isinstance(user, User) else user

    @staticmethod
    def to_billing_group(billing_group):
        if billing_group is None:
            raise SbgError('Billing group is required!')
        from sevenbridges.models.billing_group import BillingGroup
        return billing_group.id if isinstance(
            billing_group, BillingGroup) else billing_group
