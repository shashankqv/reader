# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from reader.core.models import Base, Slugged

def _get_user_model():
    try:
        # Django >= 1.5
        return settings.AUTH_USER_MODEL
    except AttributeError:
        # Django < 1.5
        return "auth.User"


class Blog(Base, Slugged):
    url = models.URLField(_("URL"), unique=True, db_index=True)
    owner = models.ForeignKey(_get_user_model(), null=True, blank=True)

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("title", "url")

    def __str__(self):
        return '{} ({})'.format(self.title, self.url)
