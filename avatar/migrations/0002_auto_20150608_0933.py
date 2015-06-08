# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloST',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SampleMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Yohoho',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('s_time', models.DateTimeField()),
                ('e_time', models.DateTimeField()),
                ('s_lat', models.FloatField()),
                ('e_lat', models.FloatField()),
                ('s_lng', models.FloatField()),
                ('e_lng', models.FloatField()),
                ('pointer', models.ManyToManyField(related_name='pointer_rel_+', to='avatar.Yohoho')),
            ],
        ),
        migrations.AlterField(
            model_name='intersection',
            name='p',
            field=models.ForeignKey(to='avatar.Point', null=True),
        ),
        migrations.AlterField(
            model_name='pathfragment',
            name='p',
            field=models.TextField(max_length=65535, null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='length',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='speed',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='road',
            name='type',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='angle',
            field=models.IntegerField(null=True),
        ),
        migrations.RemoveField(
            model_name='sample',
            name='meta',
        ),
        migrations.AlterField(
            model_name='sample',
            name='occupy',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='speed',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='src',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trajectory',
            name='path',
            field=models.ForeignKey(to='avatar.Path', null=True),
        ),
        migrations.AlterField(
            model_name='trajectory',
            name='trace',
            field=models.ForeignKey(to='avatar.Trace', null=True),
        ),
        migrations.AddField(
            model_name='clost',
            name='bounding_box',
            field=models.ForeignKey(to='avatar.Rect'),
        ),
        migrations.AddField(
            model_name='clost',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='avatar.CloST', null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='meta',
            field=models.ManyToManyField(to='avatar.SampleMeta'),
        ),
    ]
