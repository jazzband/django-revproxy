#!/usr/bin/env python

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
os.environ['REUSE_DB'] = '0'

import django

from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command


def runtests():
    if django.VERSION >= (1, 7, 0):
        django.setup()
        call_command('migrate', interactive=False)
    else:
        call_command('syncdb', interactive=False)

    call_command('flush', interactive=False)
    test_runner = get_runner(settings)
    failures = test_runner(interactive=False, failfast=False).run_tests([])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
