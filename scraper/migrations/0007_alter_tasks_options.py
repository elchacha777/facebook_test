# Generated by Django 4.2.1 on 2023-05-05 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0006_rename_concurrency_maxconcurrency_current_concurrency_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasks',
            options={'verbose_name': 'Tasks', 'verbose_name_plural': 'Tasks'},
        ),
    ]
