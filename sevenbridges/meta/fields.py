from uuid import UUID
from datetime import datetime

import six

from sevenbridges.errors import ReadOnlyPropertyError, ValidationError

empty = object()


# noinspection PyProtectedMember
class Field(object):
    def __init__(self, name=None, read_only=True, validator=None):
        self.name = name
        self.read_only = read_only
        self.validator = validator

    def __set__(self, instance, value):
        # using empty as sentinel, value can be only set once - first time
        if self.read_only and instance._data[self.name] is not empty:
            raise ReadOnlyPropertyError(
                'Property {} is marked as read only!'.format(self.name)
            )

        # handle metadata. If metadata is set use _method to signal
        # that the resource should be overwritten.
        if self.name == 'metadata':
            instance._method = 'PUT'
            if value is None:
                raise ValidationError('Not a valid dictionary!')

        value = self.validate(value)
        try:
            current_value = instance._data[self.name]
            if current_value == value:
                return
        except KeyError:
            pass
        instance._dirty[self.name] = value
        instance._data[self.name] = value

    def __get__(self, instance, cls):
        try:
            data = instance._data[self.name]
            if data and isinstance(self, DateTimeField):
                return datetime.strptime(data, '%Y-%m-%dT%H:%M:%SZ')
            else:
                return data
        except (KeyError, AttributeError):
            return None

    def validate(self, value):
        if self.validator is not None:
            return self.validator(value)
        return value


# noinspection PyProtectedMember
class CompoundField(Field):
    def __init__(self, cls, name=None, read_only=False, validator=None):
        super(CompoundField, self).__init__(
            name=name, read_only=read_only, validator=validator
        )
        self.cls = cls

    def __get__(self, instance, owner):
        data = instance._data[self.name]
        # empty is used for read only fields, None all for others
        if data is not empty and data is not None:
            return self.cls(api=instance._api, _parent=instance, **data)
        else:
            return None


# noinspection PyProtectedMember
class CompoundListField(Field):
    def __init__(self, cls, name=None, read_only=True):
        super(CompoundListField, self).__init__(name=name, read_only=read_only)
        self.cls = cls

    def __get__(self, instance, owner):
        data = instance._data[self.name]
        # empty is used for read only fields, None for all others
        if data is not empty and data is not None:
            return [self.cls(api=instance._api, **item) for item in data]
        else:
            return []


class DictField(Field, dict):
    def __init__(self, name=None, read_only=False):
        super(DictField, self).__init__(name=name, read_only=read_only)


class HrefField(Field):
    def __init__(self, name=None):
        super(HrefField, self).__init__(name=name)


class ObjectIdField(Field):
    def __init__(self, name=None, read_only=True):
        super(ObjectIdField, self).__init__(name=name, read_only=read_only)


class IntegerField(Field):
    def __init__(self, name=None, read_only=False):
        super(IntegerField, self).__init__(name=name, read_only=read_only)

    def validate(self, value):
        if value and not isinstance(value, six.integer_types):
            raise ValidationError(
                '{} is not a valid value for {}'.format(
                    value, self.__class__.__name__
                )
            )
        return value


class FloatField(Field):
    def __init__(self, name=None, read_only=False):
        super(FloatField, self).__init__(name=name, read_only=read_only)

    def validate(self, value):
        try:
            return float(value)
        except ValueError:
            raise ValidationError(
                '{} is not a valid value for {}'.format(
                    value, self.__class__.__name__
                )
            )


class StringField(Field):
    def __init__(self, name=None, read_only=False, max_length=None):
        super(StringField, self).__init__(name=name, read_only=read_only)
        self.max_length = max_length

    def validate(self, value):
        value = super(StringField, self).validate(value)
        if value and not isinstance(value, six.string_types):
            raise ValidationError(
                '{} is not a valid value for {}'.format(
                    value, self.__class__.__name__)
            )
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                '{}: max length exceeded.'.format(self.name))
        return value


class DateTimeField(Field):
    def __init__(self, name=None, read_only=True):
        super(DateTimeField, self).__init__(name=name, read_only=read_only)


class BooleanField(Field):
    def __init__(self, name=None, read_only=False):
        super(BooleanField, self).__init__(name=name, read_only=read_only)

    def validate(self, value):
        if value and not isinstance(value, bool):
            raise ValidationError(
                '{} is not a valid value for {}'.format(
                    value, self.__class__.__name__
                )
            )
        return value


class UuidField(Field):
    def __init__(self, name=None, read_only=True):
        super(UuidField, self).__init__(name=name, read_only=read_only)

    def validate(self, value):
        value = super(UuidField, self).validate(value)
        try:
            UUID(value, version=4)
            return value
        except ValueError:
            raise ValidationError(
                '{} is not a valid value for {}'.format(
                    value, self.__class__.__name__)
            )


class BasicListField(Field):
    def __init__(self, name=None, read_only=False, max_length=None):
        super(BasicListField, self).__init__(name=name,
                                             read_only=read_only)
        self.max_length = max_length

    def validate(self, value):
        value = super(BasicListField, self).validate(value)
        if value and not isinstance(value, list):
            raise ValidationError('Validation failed, not a list.')
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                'Exceeded {} allowed elements.'.format(self.max_length)
            )
        return value
