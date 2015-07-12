# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0012_auto_20150711_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='clost',
            name='endtime',
            field=models.DateTimeField(null=True),
        ),
    ]
