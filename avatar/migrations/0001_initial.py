# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
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
                ('p', models.TextField(max_length=65535)),
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
            name='Road',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('type', models.IntegerField()),
                ('length', models.IntegerField()),
                ('speed', models.IntegerField()),
                ('intersection', models.ManyToManyField(to='avatar.Intersection')),
                ('p', models.ManyToManyField(to='avatar.Point')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.CharField(max_length=36, serialize=False, primary_key=True)),
                ('t', models.DateTimeField()),
                ('speed', models.IntegerField()),
                ('angle', models.IntegerField()),
                ('occupy', models.IntegerField()),
                ('meta', models.CharField(max_length=255)),
                ('src', models.IntegerField()),
                ('p', models.ForeignKey(to='avatar.Point')),
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
                ('path', models.ForeignKey(to='avatar.Path')),
                ('trace', models.ForeignKey(to='avatar.Trace')),
            ],
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
            field=models.ForeignKey(to='avatar.Point'),
        ),
    ]
