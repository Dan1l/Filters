# coding: utf-8

import copy
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict

from . import updaters


def get_declared_subfilters(bases, attrs, with_base_fields=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metaclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions.
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(six.iteritems(attrs)) if
              isinstance(obj, updaters.BaseUpdater)]
    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = list(six.iteritems(base.base_fields)) + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = list(six.iteritems(base.declared_fields)) + fields

    return OrderedDict(fields)


class DeclarativeSubFiltersMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(mcs, name, bases, attrs):
        attrs['base_fields'] = get_declared_subfilters(bases, attrs)
        new_class = super(DeclarativeSubFiltersMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class


class BaseFilter(object):
    creation_counter = 0
    bound = None
    error = False
    title = None

    def __init__(self, title):
        self.title = title
        self.updaters = copy.deepcopy(self.base_fields)
        self.creation_counter = Filter.creation_counter
        Filter.creation_counter += 1

    def update_qs(self, qs, name, data=None, initial=None):
        for uname, u in self.updaters.items():
            qs = u.proceed(name, None, qs)
        initial = initial if initial is not None else {}
        if data is not None:
            data_name = '_'.join([name, 'filter'])
            if data_name in data:
                self.bound = data.get(data_name)
                updater = self.updaters[data.get(data_name)]
                qs = updater.proceed(name, data, qs)
                if updater.error:
                    self.error = True
            elif data_name in initial:
                updater = self.updaters[initial.get(data_name)]
                qs = updater.proceed(name, initial, qs)
        return qs


class Filter(six.with_metaclass(DeclarativeSubFiltersMetaclass, BaseFilter)):
    """A collection of Filters, plus their associated data."""


class BaseStringFilter(Filter):
    equal = updaters.CharEqual(_('Equal'))
    starts_with = updaters.StartsWith(_('Starts with'))
    ends_with = updaters.EndsWith(_('Ends with'))
    contains = updaters.Contains(_('Contains'))


class StringFilterWithEmpty(BaseStringFilter):
    empty = updaters.Empty(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))


class StringFilterWithEmptyForIntegerField(BaseStringFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotEmpty(_('Filled'))


class BaseIntegerFilter(Filter):
    equal = updaters.IntegerEqual(_('Equal'))
    greater_than = updaters.GreaterThan(_('Greater than'))
    less_than = updaters.LessThan(_('Less than'))


class IntegerFilterWithEmpty(BaseIntegerFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))


class BaseDateFilter(Filter):
    today = updaters.DateToday(_('Today'))
    equal = updaters.DateEqual(_('Equal'))
    range = updaters.DateRange(_('Between'))


class DateFilterWithEmpty(BaseDateFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))


class BaseDateTimeFilter(Filter):
    today = updaters.DateTimeToday(_('Today'))
    equal = updaters.DateTimeEqual(_('Equal'))
    range = updaters.DateTimeRange(_('Between'))


class DateTimeFilterWithEmpty(BaseDateTimeFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))


class BooleanFilter(Filter):
    true = updaters.TrueBoolean(_('Checked'))
    false = updaters.FalseBoolean(_('Not checked'))


class BaseChoiceFilter(Filter):
    choice_equal = updaters.Choice(_('Equal'))
    choices = None

    def __init__(self, title, choices, select2=False):
        super(BaseChoiceFilter, self).__init__(title)
        self.choices = choices
        for name, u in self.updaters.items():
            if isinstance(u, updaters.ChoiceIn) or isinstance(u, updaters.Choice):
                u.queryset = self.choices
                u.select2 = select2


class ChoiceFilterWithEmpty(BaseChoiceFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))


class BaseModelChoiceFilter(Filter):
    choice_equal = updaters.ModelChoice(_('Equal'))
    queryset = None

    def __init__(self, title, queryset, select2=False):
        super(BaseModelChoiceFilter, self).__init__(title)
        self.queryset = queryset

        for name, u in self.updaters.items():
            if isinstance(u, updaters.ModelChoice):
                u.queryset = self.queryset
                u.select2 = select2


class ModelChoiceFilterWithEmpty(BaseModelChoiceFilter):
    empty = updaters.IsNull(_('Empty'))
    not_empty = updaters.NotNull(_('Filled'))
