# encoding: utf-8
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import get_template
from django.db.models import Q
from django import forms
from django.utils.translation import ugettext_lazy as _


class EmptyForm(forms.Form):
    pass


class CharForm(forms.Form):
    value = forms.CharField(label=_('Value'), max_length=255)


class DateRangeForm(forms.Form):
    start = forms.DateField(label=_('Start'))
    end = forms.DateField(label=_('End'))


class IntegerForm(forms.Form):
    value = forms.IntegerField(label=_('Value'))


class DateForm(forms.Form):
    value = forms.DateField(label=_('Date'))


class ChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('queryset')
        select2 = kwargs.pop('select2', False)
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.queryset = qs
        self.select2 = select2
        self.fields['value'] = forms.ChoiceField(label=_('Choice'), choices=qs)


class ChoiceMultiForm(forms.Form):
    values = forms.MultipleChoiceField(label=_('Values'))


class ModelChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('queryset')
        select2 = kwargs.pop('select2')
        super(ModelChoiceForm, self).__init__(*args, **kwargs)
        self.queryset = qs
        self.select2 = select2
        self.fields['value'] = forms.ModelChoiceField(label=_('Choice'), queryset=qs)


class BaseUpdater(object):
    creation_counter = 0
    form = None
    formclass = None
    name = None
    template = 'ww_filters/default.html'
    error = False

    def __init__(self, title):
        self.title = title
        self.creation_counter = BaseUpdater.creation_counter
        BaseUpdater.creation_counter += 1

    def render(self):
        tpl = get_template(self.template)
        c = Context({'form': self.form})
        return tpl.render(c)

    def update_qs(self, qs):
        pass

    def proceed(self, name, data, qs):
        self.name = name
        self.form = self.formclass(data, prefix=name + '_filter')
        if self.form.is_valid():
            qs = self.update_qs(qs)
        elif data is not None:
            self.error = True
        return qs


class CharEqual(BaseUpdater):
    formclass = CharForm

    def update_qs(self, qs):
        return qs.filter(**{
            self.name: self.form.cleaned_data['value']
        })


class StartsWith(BaseUpdater):
    formclass = CharForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'istartswith']): self.form.cleaned_data['value']
        })


class EndsWith(BaseUpdater):
    formclass = CharForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'iendswith']): self.form.cleaned_data['value']
        })


class Contains(BaseUpdater):
    formclass = CharForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'icontains']): self.form.cleaned_data['value']
        })


class ModelChoice(BaseUpdater):
    formclass = ModelChoiceForm
    queryset = None

    def proceed(self, name, data, qs):
        self.name = name
        self.form = self.formclass(data, queryset=self.queryset, prefix=name + '_filter',
                                   select2=getattr(self, 'select2', None))
        if self.form.is_valid():
            qs = self.update_qs(qs)
        elif data is not None:
            self.error = True
        return qs

    def update_qs(self, qs):
        return qs.filter(**{
            self.name: self.form.cleaned_data['value']
        })


class Choice(BaseUpdater):
    formclass = ChoiceForm
    queryset = None

    def proceed(self, name, data, qs):
        self.name = name
        self.form = self.formclass(data, queryset=self.queryset, prefix=name + '_filter',
                                   select2=getattr(self, 'select2', None))
        if self.form.is_valid():
            qs = self.update_qs(qs)
        elif data is not None:
            self.error = True
        return qs

    def update_qs(self, qs):
        return qs.filter(**{
            self.name: self.form.cleaned_data['value']
        })


class ChoiceIn(BaseUpdater):
    formclass = ChoiceMultiForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'in']): self.form.cleaned_data['value']
        })


class DateRange(BaseUpdater):
    formclass = DateRangeForm
    template = 'ww_filters/daterange.html'

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'range']): [self.form.cleaned_data['start'], self.form.cleaned_data['end']]
        })


class DateEqual(BaseUpdater):
    formclass = DateForm
    template = 'ww_filters/date.html'

    def update_qs(self, qs):
        return qs.filter(**{
            self.name: self.form.cleaned_data['value']
        })


class DateToday(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        from datetime import date

        return qs.filter(**{
            self.name: date.today()
        })


class DateTimeRange(BaseUpdater):
    formclass = DateRangeForm
    template = 'ww_filters/daterange.html'

    def update_qs(self, qs):
        import datetime

        return qs.filter(**{
            '__'.join([self.name, 'range']): [
                datetime.datetime.combine(self.form.cleaned_data['start'], datetime.time.min),
                datetime.datetime.combine(self.form.cleaned_data['end'], datetime.time.max)
            ]
        })


class DateTimeEqual(BaseUpdater):
    formclass = DateForm
    template = 'ww_filters/date.html'

    def update_qs(self, qs):
        import datetime

        return qs.filter(**{
            '__'.join([self.name, 'range']): [
                datetime.datetime.combine(self.form.cleaned_data['value'], datetime.time.min),
                datetime.datetime.combine(self.form.cleaned_data['value'], datetime.time.max)
            ]
        })


class DateTimeToday(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        import datetime

        return qs.filter(**{
            '__'.join([self.name, 'range']): [
                datetime.datetime.combine(datetime.date.today(), datetime.time.min),
                datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            ]
        })


class IntegerEqual(BaseUpdater):
    formclass = IntegerForm

    def update_qs(self, qs):
        return qs.filter(**{
            self.name: self.form.cleaned_data['value']
        })


class LessThan(BaseUpdater):
    formclass = IntegerForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'lt']): self.form.cleaned_data['value']
        })


class GreaterThan(BaseUpdater):
    formclass = IntegerForm

    def update_qs(self, qs):
        return qs.filter(**{
            '__'.join([self.name, 'gt']): self.form.cleaned_data['value']
        })


class IsNull(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(**{'__'.join([self.name, 'isnull']): True})


class NotNull(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(**{'__'.join([self.name, 'isnull']): False})


class Empty(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(Q(**{'__'.join([self.name, 'isnull']): True}) | Q(**{self.name: u''}))


class NotEmpty(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(Q(**{'__'.join([self.name, 'isnull']): False}) & ~Q(**{self.name: u''}))


class AllDirectory(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs


class TrueBoolean(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(**{self.name: True})


class FalseBoolean(BaseUpdater):
    formclass = EmptyForm

    def update_qs(self, qs):
        return qs.filter(**{self.name: False})
