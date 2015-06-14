# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0005_auto_20150614_0457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clost',
            name='context',
            field=models.CharField(max_length=65535, null=True),
        ),
    ]
