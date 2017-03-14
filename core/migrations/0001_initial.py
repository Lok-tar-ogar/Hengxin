# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-14 07:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='文章标题')),
                ('coverImg', models.CharField(blank=True, max_length=50, null=True, verbose_name='封面图片的地址')),
                ('content', models.TextField(verbose_name='文章详情')),
                ('innerImgs', models.CharField(blank=True, max_length=1000, null=True, verbose_name='图片们的地址')),
                ('viewedTimes', models.IntegerField(verbose_name='浏览次数')),
                ('type', models.CharField(blank=True, max_length=50, null=True, verbose_name='文章类型')),
                ('dimDate', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-dimDate'],
                'verbose_name': '文章',
            },
        ),
        migrations.CreateModel(
            name='carousel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='标题')),
                ('img', models.CharField(max_length=50, verbose_name='图片（1920*600）')),
                ('link', models.CharField(blank=True, max_length=50, verbose_name='链接地址（可为空）')),
                ('caption', models.CharField(blank=True, max_length=500, null=True, verbose_name='子标题')),
                ('dimDate', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-dimDate'],
                'verbose_name': '轮播管理',
            },
        ),
    ]
