#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from reader.core.utils import extract_data_from_feed_url


class Command(BaseCommand):
    help = "Add a complete blog feed to our db."
    args = "<feed_url>"

    def handle(self, *args, **options):
    ¦   feed_url = args[0]
        extract_data_from_feed_url(feed_url)
