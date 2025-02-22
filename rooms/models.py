from django.core.validators import MinValueValidator
from django.db import models
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
        return self.rooms.filter(status='available').count()

    # 价格最多8位，小数2位 validators=[MinValueValidator(0)]小于0，则验证失败
    base_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0.00, verbose_name="基础价格（元）")
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="加价（元）")

    @property
    def weekday_price(self):
        return self.base_price

    @property
    def weekend_price(self):
        return self.extra_price + self.base_price


    # 入住
    expected_check_in = models.TimeField(null=True, blank=True, verbose_name='入住时间', default='14:00:00')

    # 退房
    expected_check_out = models.TimeField(null=True, blank=True, verbose_name='退房时间', default='12:00:00')


    introduction = models.TextField(blank=True, verbose_name="房型介绍")




class Room(models.Model):
    ROOM_STATUS = (
        ('available', '空闲'),
        ('booked', '已预订'),
        ('check_in', '已入住'),
        ('maintenance', '维护中'),
        ('cleaning', '打扫中'),
        ('prepared', '备房'),
    )

    room_id = models.IntegerField(unique=True, primary_key=True, verbose_name='房间号')

    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms', verbose_name='房间类型')

    floor = models.IntegerField(null=True, blank=True, verbose_name="楼层")

    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available', verbose_name="房间状态")


    class Meta:
        ordering = ['room_id']

    def __str__(self):
        return f"{self.room_id} - {self.room_type.type_name}"
