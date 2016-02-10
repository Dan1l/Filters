# coding: utf-8

import copy
from django.utils import six
from collections import OrderedDict

from . import filters


def get_declared_filters(bases, attrs, with_base_filters=True):

    filters = [(filter_name, attrs.pop(filter_name))
              for filter_name, obj in list(six.iteritems(attrs)) if isinstance(obj, filters.BaseFilter)]
    filters.sort(key=lambda x: x[1].creation_counter)

    if with_base_filters:
        for base in bases[::-1]:
            if hasattr(base, 'base_filters'):
                filters = list(six.iteritems(base.base_filters)) + filters
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_filters'):
                filters = list(six.iteritems(base.declared_filters)) + filters

    return OrderedDict(filters)


class DeclarativeFilterCollectionMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        attrs['base_filters'] = get_declared_filters(bases, attrs)
        new_class = super(DeclarativeFilterCollectionMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class


class BaseFilterCollection(object):
    filters = {}
    qs = None
    initial = None

    def __init__(self, qs, data=None, initial=None):
        self.filters = copy.deepcopy(self.base_filters)
        self.data = data
        self.qs = qs
        self.initial = initial

    def update_qs(self):
        if self.data is None and self.initial is None:
            return self.qs
        qs = self.qs
        for filter_name in self.filters:
            qs = self.filters[filter_name].update_qs(qs, filter_name, self.data, self.initial)
        return qs


class FilterCollection(six.with_metaclass(DeclarativeFilterCollectionMetaclass, BaseFilterCollection)):
    pass


class ModelFilterCollectionOptions(object):
    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.fields = getattr(options, 'fields', None)
        self.exclude = getattr(options, 'exclude', None)
        self.titles = getattr(options, 'titles', None)
        self.select2 = getattr(options, 'select2', None)


class ModelFilterCollectionMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(ModelFilterCollectionMetaclass, cls).__new__(cls, name, bases, attrs)
        declared_fields = get_declared_filters(bases, attrs, False)

        opts = new_class._meta = ModelFilterCollectionOptions(getattr(new_class, 'Meta', None))
        fields = opts.fields
        exclude = opts.exclude
        filter_fields = OrderedDict()

        if opts.model:
            from django.db.models.fields import Field as ModelField, related
            from django.db.models import fields as fields_
            sortable_virtual_fields = [f for f in opts.model._meta.virtual_fields if isinstance(f, ModelField)]
            for f in sorted(list(opts.model._meta.concrete_fields) + sortable_virtual_fields):
                if fields is not None and not f.name in fields:
                    continue
                if exclude and f.name in exclude:
                    continue
                if opts.titles is not None and f.name in opts.titles:
                    title = opts.titles[f.name]
                else:
                    title = f.verbose_name
                if opts.select2 is not None and f.name in opts.select2:
                    select2 = True
                else:
                    select2 = False

                if isinstance(f, (related.ForeignKey, )):
                    if f.blank:
                        filter_fields[f.name] = filters.ModelChoiceFilterWithEmpty(
                            title=title, select2=select2, queryset=f.rel.to._default_manager.all())
                    else:
                        filter_fields[f.name] = filters.BaseModelChoiceFilter(
                            title=title, select2=select2, queryset=f.rel.to._default_manager.all())

                elif f.choices:
                    if f.blank:
                        filter_fields[f.name] = filters.ChoiceFilterWithEmpty(title=title, choices=f.choices,
                                                                              select2=select2)
                    else:
                        filter_fields[f.name] = filters.BaseChoiceFilter(title=title, choices=f.choices, select2=select2)

                elif isinstance(f, (fields_.CharField, fields_.TextField)):
                    if f.blank:
                        filter_fields[f.name] = filters.StringFilterWithEmpty(title=title)
                    else:
                        filter_fields[f.name] = filters.BaseStringFilter(title=title)

                elif isinstance(f, (fields_.IntegerField, fields_.DecimalField, fields_.FloatField)):
                    if f.blank:
                        filter_fields[f.name] = filters.IntegerFilterWithEmpty(title=title)
                    else:
                        filter_fields[f.name] = filters.BaseIntegerFilter(title=title)

                elif isinstance(f, fields_.DateTimeField):
                    if f.blank:
                        filter_fields[f.name] = filters.DateTimeFilterWithEmpty(title=title)
                    else:
                        filter_fields[f.name] = filters.BaseDateTimeFilter(title=title)

                elif isinstance(f, fields_.DateField):
                    if f.blank:
                        filter_fields[f.name] = filters.DateFilterWithEmpty(title=title)
                    else:
                        filter_fields[f.name] = filters.BaseDateFilter(title=title)

                elif isinstance(f, fields_.BooleanField):
                    filter_fields[f.name] = filters.BooleanFilter(title=title)

            filter_fields.update(declared_fields)

            if fields is not None:
                sorted_filter_fields = OrderedDict()
                for field in fields:
                    sorted_filter_fields[field] = filter_fields.pop(field)
                sorted_filter_fields.update(filter_fields)
                new_class.base_filters = sorted_filter_fields
            else:
                new_class.base_filters = filter_fields
        else:
            new_class.base_filters = declared_fields
        return new_class


class BaseModelFilterCollection(BaseFilterCollection):
    def __init__(self, qs, data=None, initial=None):
        super(BaseModelFilterCollection, self).__init__(qs, data, initial)


class ModelFilterCollection(six.with_metaclass(ModelFilterCollectionMetaclass, BaseModelFilterCollection)):
    pass
