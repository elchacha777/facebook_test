# Generated by Django 4.2.1 on 2023-05-12 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0018_remove_tasks_is_running'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasks',
            name='cache_time',
            field=models.IntegerField(default=0),
        ),
    ]
