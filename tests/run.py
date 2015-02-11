#!/usr/bin/env python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

import django

from django.test.utils import get_runner
from django.conf import settings


def runtests():
    if django.VERSION >= (1, 7, 0):
        django.setup()

    test_runner = get_runner(settings)
    failures = test_runner(interactive=False, failfast=False).run_tests([])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
