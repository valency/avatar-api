# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CloST',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('haschild', models.IntegerField(null=True)),
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
            name='Intersection',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PathFragment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p', models.TextField(max_length=65535, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
            ],
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
            name='Road',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('type', models.IntegerField(null=True)),
                ('length', models.IntegerField(null=True)),
                ('speed', models.IntegerField(null=True)),
                ('intersection', models.ManyToManyField(to='avatar.Intersection')),
                ('p', models.ManyToManyField(to='avatar.Point')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('t', models.DateTimeField()),
                ('speed', models.IntegerField(null=True)),
                ('angle', models.IntegerField(null=True)),
                ('occupy', models.IntegerField(null=True)),
                ('src', models.IntegerField(null=True)),
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
            name='Trace',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('p', models.ManyToManyField(to='avatar.Sample')),
            ],
        ),
        migrations.CreateModel(
            name='Trajectory',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('taxi', models.CharField(max_length=255)),
                ('path', models.ForeignKey(to='avatar.Path', null=True)),
                ('trace', models.ForeignKey(to='avatar.Trace', null=True)),
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
        migrations.AddField(
            model_name='sample',
            name='meta',
            field=models.ManyToManyField(to='avatar.SampleMeta'),
        ),
        migrations.AddField(
            model_name='sample',
            name='p',
            field=models.ForeignKey(to='avatar.Point'),
        ),
        migrations.AddField(
            model_name='pathfragment',
            name='road',
            field=models.ForeignKey(to='avatar.Road'),
        ),
        migrations.AddField(
            model_name='path',
            name='road',
            field=models.ManyToManyField(to='avatar.PathFragment'),
        ),
        migrations.AddField(
            model_name='intersection',
            name='p',
            field=models.ForeignKey(to='avatar.Point', null=True),
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
    ]
