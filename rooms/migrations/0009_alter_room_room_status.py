# Generated by Django 5.1.5 on 2025-03-14 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0008_room_expected_check_in_room_expected_check_out_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_status',
            field=models.CharField(choices=[('available', '空闲'), ('booked', '已预订'), ('checked_in', '已入住'), ('cleaning', '打扫中'), ('maintenance', '维护中'), ('prepared', '备房')], default='available', max_length=20, verbose_name='房间状态'),
        ),
    ]
