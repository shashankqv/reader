# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Base(models.Model):
    title = models.CharField(_("Title"), max_length=255, blank=True,
                             db_index=True)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Last Modified"). auto_now=True)


class Slugged(models.Model):
    slug = models.SlugField(max_length=255, db_index=True)
