# Generated by Django 2.1.5 on 2019-01-31 21:26

import datetime
from django.db import migrations
from django.utils.timezone import utc
import unixtimestampfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0002_auto_20190130_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date',
            field=unixtimestampfield.fields.UnixTimeStampField(default=datetime.datetime(2019, 1, 31, 21, 26, 14, 990924, tzinfo=utc)),
        ),
    ]
