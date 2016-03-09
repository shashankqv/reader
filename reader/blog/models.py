# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from reader.core.models import Base, Slugged, UUID
from reader.categories.models import Category
from reader.profiles.models import Author

def _get_user_model():
    try:
        # Django >= 1.5
        return settings.AUTH_USER_MODEL
    except AttributeError:
        # Django < 1.5
        return "auth.User"


@python_2_unicode_compatible
class Blog(Base, Slugged):
    url = models.URLField(_("URL"), unique=True, db_index=True)
    owner = models.ForeignKey(_get_user_model(), null=True, blank=True)

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("title", "url")

    def __str__(self):
        return '{} ({})'.format(self.title, self.url)


@python_2_unicode_compatible
class Feed(Base):
    blog = models.ForeignKey(Blog, null=True, blank=True)
    site = models.ForeignKey(Site, null=True, blank=True, db_index=True)
    category = models.ForeignKey(Category, blank=True, null=True,
                                 db_index=True)
    url = models.URLField(_("Url"), unique=True, db_index=True)
    subtitle = models.TextField(_("Subtitle"), blank=True, null=True)
    rights = models.CharField(_("Rights"), max_length=255, blank=True,
                              null=True)
    info = models.CharField(_("Infos"), max_length=255, blank=True, null=True)
    language = models.CharField(_("Language"), max_length=50, blank=True,
                                null=True)
    icon_url = models.URLField(_("Icon URL"), blank=True, null=True)
    image_url = models.URLField(_("Image URL"), blank=True, null=True)

    # etag attribute from Feedparser's Feed object
    etag = models.CharField(_("Etag"), max_length=50, blank=True,
        null=True, db_index=True)
    # datetime when the feed was checked by last time
    last_checked = models.DateTimeField(_("Last checked"), null=True,
                                        blank=True)
    # in order to retrieve it or not
    is_active = models.BooleanField(_("Is active"), default=True,
                                    db_index=True,
        help_text=_("If disabled, this feed will not be further updated."))

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")
        ordering = ('title', )

    def save(self, *args, **kwargs):
        if not self.blog:
            self.modified = self.etag = None

            try:
                USER_AGENT = settings.PLANET["USER_AGENT"]
            except (KeyError, AttributeError):
                print("""Please set the PLANET = {"USER_AGENT": <string>} in your settings.py""")
                exit(0)

            document = feedparser.parse(self.url, agent=USER_AGENT,
                                        modified=self.modified, etag=self.etag)

            self.site = Site.objects.get(pk=settings.SITE_ID)

            self.title = document.feed.get("title", "--")
            self.subtitle = document.feed.get("subtitle")
            blog_url = document.feed.get("link")
            self.rights = document.feed.get("rights") or document.feed.get("license")
            self.info = document.feed.get("info")
            self.guid = document.feed.get("id")
            self.image_url = document.feed.get("image", {}).get("href")
            self.icon_url = document.feed.get("icon")
            self.language = document.feed.get("language")
            self.etag = document.get("etag", '')

            self.last_modified = document.get("updated_parsed", datetime.now())
            if isinstance(self.last_modified, struct_time):
                self.last_modified = datetime.fromtimestamp(mktime(self.last_modified))

            self.blog, created = Blog.objects.get_or_create(
                url=blog_url, defaults={"title": self.title})

        super(Feed, self).save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.title, self.url)


@python_2_unicode_compatible
class PostAuthorData(Base):
    pass


@python_2_unicode_compatible
class Post(Base, Slugged, UUID):
    authors = models.ManyToManyField(Author, through=PostAuthorData)
    feed = models.ForeignKey(Feed, null=False, blank=False)
    content = models.TextField(_("Content"))
    comments_url = models.URLField(_("Comments URL"), null=True, blank=True)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ("timestamp", "last_modified")
        unique_together = (('feed', 'uuid'),)

    def __str__(self):
        return "{} ({})".format(self.title, self.feed.title)


