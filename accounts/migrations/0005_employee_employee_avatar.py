# Generated by Django 5.1.5 on 2025-02-24 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_employee_is_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='employee_avatar',
            field=models.ImageField(default='user_avatar.jpg', upload_to='employee_avatar/', verbose_name='头像'),
        ),
    ]
