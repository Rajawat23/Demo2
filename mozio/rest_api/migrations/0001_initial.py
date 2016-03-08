# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djgeojson.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geos', djgeojson.fields.PolygonField(default=dict)),
                ('Name', models.TextField()),
                ('Price', models.DecimalField(max_digits=7, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Name', models.TextField()),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\+?1?\\d{9,15}$', message=b"Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])),
                ('Language', models.CharField(max_length=10)),
                ('Currency', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='Service_id',
            field=models.ForeignKey(to='rest_api.ServiceProfile'),
        ),
    ]
