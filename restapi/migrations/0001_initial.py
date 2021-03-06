# Generated by Django 3.1 on 2020-08-11 21:18

import datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50, unique=True)),
                ('user_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TokenStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.CharField(max_length=50, unique=True)),
                ('user_id', models.IntegerField()),
                ('status', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('place', models.CharField(max_length=50)),
                ('uri', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2020, 8, 11, 21, 18, 37, 268356), max_length=50)),
                ('user_id', models.IntegerField()),
                ('shared_with', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(to='restapi.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('user_id', models.IntegerField()),
                ('images', models.ManyToManyField(to='restapi.Image')),
                ('shared_with', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
