# encoding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class SavedFilters(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('User'))
    name = models.CharField(max_length=100, verbose_name=_('Filter Name'))
    data = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    type = models.CharField(max_length=30)
