# Generated by Django 5.1.5 on 2025-03-16 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_expected_check_in_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='occupants_count',
            field=models.PositiveIntegerField(default=0, verbose_name='入住人数'),
        ),
    ]
