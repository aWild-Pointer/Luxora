# Generated by Django 5.1.5 on 2025-02-20 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='check_in_time',
            new_name='expected_check_in',
        ),
        migrations.RenameField(
            model_name='room',
            old_name='check_out_time',
            new_name='expected_check_out',
        ),
    ]
