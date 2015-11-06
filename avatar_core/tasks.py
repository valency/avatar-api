from __future__ import absolute_import

import time

from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task()
def heavy_task():
    time.sleep(10)
    return "time's tough."
