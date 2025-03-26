from datetime import datetime
from itertools import count

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, When, IntegerField, Count

from accounts.models import Homestay


class RoomType(models.Model):
    # 自动生成
    type_id = models.AutoField(primary_key=True, unique=True, verbose_name='房型id')

    type_name = models.CharField(max_length=50, unique=True, default="default", verbose_name='房型名称')

    homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE,
                                 related_name='room_types', verbose_name='所属民宿')

    capacity = models.PositiveIntegerField(verbose_name="入住人数", default="2")

    # total = models.IntegerField(default=0, verbose_name='总房间数')
    @property
    def total(self):
        # 计算该房间类型关联的所有房间数量
        return self.rooms.count()

    # remaining = models.IntegerField(default=0, verbose_name='剩余房间数')
    @property
    def remaining(self):
        # 计算该房间类型中状态为 'available' 的房间数量
        # return self.rooms.filter(room_status='available').count()
        return self.rooms.exclude(room_status__in=['maintenance', 'prepared']).count()

    # 价格最多8位，小数2位 validators=[MinValueValidator(0)]小于0，则验证失败
    base_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0.00, verbose_name="基础价格（元）")
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="加价（元）")

    @property
    def weekday_price(self):
        return self.base_price

    @property
    def weekend_price(self):
        return self.extra_price + self.base_price

    @property
    def status_counts(self):
        # 1. 取出所有可能的状态（例如从模型 choices 里取）
        all_statuses = [choice[0] for choice in Room.ROOM_STATUS]

        # 2. 数据库实际存在的状态计数
        qs = self.rooms.values('room_status').annotate(count=Count('room_status'))

        # 3. 初始化一个字典，让所有状态默认计数 0
        counts = {status: 0 for status in all_statuses}

        # 4. 用查询到的聚合结果进行覆盖
        for entry in qs:
            counts[entry['room_status']] = entry['count']

        return counts


    # 入住
    expected_check_in = models.TimeField(null=True, blank=True, verbose_name='入住时间', default='14:00:00')

    # 退房
    expected_check_out = models.TimeField(null=True, blank=True, verbose_name='退房时间', default='12:00:00')


    introduction = models.TextField(blank=True, verbose_name="房型介绍")

    class Meta:
        ordering = ['base_price', 'extra_price']

    def __str__(self):
        return self.type_name



class Room(models.Model):
    ROOM_STATUS = (
        ('available', '空闲'),
        ('booked', '已预订'),
        ('checked_in', '已入住'),
        ('cleaning', '打扫中'),
        ('maintenance', '维护中'),
        ('prepared', '备房'),
    )

    room_id = models.AutoField(unique=True, primary_key=True, verbose_name='房间id')

    room_number = models.CharField(max_length=20, verbose_name='房号')

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='房间类型'
    )

    room_status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available', verbose_name="房间状态")


    # 排序
    class Meta:
        ordering = [
            Case(
                When(room_status='available', then=0),
                When(room_status='booked', then=1),
                When(room_status='check_in', then=2),
                When(room_status='cleaning', then=3),
                When(room_status='maintenance', then=4),
                When(room_status='prepared', then=5),
                default=6,
                output_field=IntegerField()
            ),
            'room_number',

        ]

    @property
    def get_current_order(self):
        today = datetime.now().date()
        order = self.orders.filter(
            order_status__in=['checked_in'],
            expected_check_in_date__lte=today,
            expected_check_out_date__gte=today
        ).first()
        return order.order_id if order else None

    def __str__(self):
        return f"{self.room_number} ({self.room_type.type_name})"



