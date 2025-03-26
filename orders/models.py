from datetime import datetime

from django.db import models

from accounts.models import Homestay
from rooms.models import RoomType, Room

class Occupant(models.Model):
    """
    入住人表，用于保存单个入住人的信息。
    """
    id_card = models.CharField(
        max_length=30,
        # 冗余，考虑护照等
        primary_key=True,
        verbose_name="身份证",
    )
    name = models.CharField(max_length=100, verbose_name="入住人姓名")
    phone = models.CharField(max_length=11, verbose_name="手机号", blank=True, null=True)
    # 如果需要记录更多信息，可以在此扩展字段，如年龄、性别、会员等级等

    def __str__(self):
        return f"入住人: {self.name}, 身份证: {self.id_card}"



class Order(models.Model):
    STATUS = (
        ('booked', '已预订'),
        ('checked_in', '已入住'),
        ('checked_out', '已退房'),
        ('cancelled', '已取消'),
        ('finished', '已完成'),
    )
    CHANNELS = (
        ('online', '线上支付'),
        ('advance', '预付'),
        ('in_store', '到店支付'),
        ('others', '其他'),
    )
    METHODS = (
        ('cash', '现金'),
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank_transfer', '银行转账'),
        ('others', '其他'),
    )

    order_id = models.AutoField(primary_key=True, verbose_name='订单id')
    order_status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='booked',
        verbose_name="订单状态"
    )

    # 绑定民宿
    homestay = models.ForeignKey(
        Homestay,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='所属民宿'
    )

    # 如果系统需要区分下单人与入住人，可分开多个字段
    customer_name = models.CharField(max_length=100, verbose_name="下单人姓名")
    customer_phone = models.CharField(max_length=11, verbose_name="下单人手机号")
    customer_IDcard = models.CharField(max_length=30, verbose_name="下单人身份证")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="订单创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="订单更新时间")

    check_in_datetime = models.DateTimeField(blank=True, null=True, verbose_name="实际入住时间")
    check_out_datetime = models.DateTimeField(blank=True, null=True, verbose_name="实际退房时间")

    expected_check_in_date = models.DateField(blank=True, null=True, verbose_name="预期入住日期")
    expected_check_out_date = models.DateField(blank=True, null=True, verbose_name="预期退房日期")

    expected_check_in_time = models.TimeField(blank=True, null=True, verbose_name="预期到店时间")
    expected_check_out_time = models.TimeField(blank=True, null=True, verbose_name="预期离店时间")

    expected_check_in_datetime = models.DateTimeField(blank=True, null=True, verbose_name="预期入住日期-时间")
    expected_check_out_datetime = models.DateTimeField(blank=True, null=True, verbose_name="预期退房日期-时间")

    payment_time = models.DateTimeField(blank=True, null=True, verbose_name="支付时间")



    # 必须是整数
    days = models.PositiveIntegerField(default=1, verbose_name="入住天数")
    # 快照字段，用于记录订单创建时的房间号
    room_number_snapshot = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='房间号(下单时)'
    )
    # 快照字段，用于记录订单创建时的房型
    room_type_snapshot = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='房型(下单时)'
    )
    # 房间 & 房型
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        verbose_name='房号'
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        verbose_name='房型'
    )
    # 订单与入住人是多对多
    occupants = models.ManyToManyField(
        Occupant,
        related_name='orders',
        blank=True,
    )
    occupants_count = models.PositiveIntegerField(default=0, verbose_name="入住人数")


    is_pay = models.BooleanField(default=False, verbose_name="是否支付")

    amounts = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="订单金额")

    payment_channel = models.CharField(max_length=20, choices=CHANNELS, blank=True, null=True, default='others', verbose_name="支付渠道")

    payment_method = models.CharField(max_length=20, choices=METHODS, blank=True, null=True, default='cash', verbose_name="支付方式")

    # 冗余字段，用于更改订单等操作
    related_order = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='关联订单',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        """
        在保存时，就把房间号自动写到room_number_snapshot，
        可以在这里做判断。
        """
        # 每次都更新快照，使其与当前外键保持一致
        if self.room:
            self.room_number_snapshot = self.room.room_number
        else:
            self.room_number_snapshot = None

        if self.room_type:
            self.room_type_snapshot = self.room_type.type_name
        else:
            self.room_type_snapshot = None



        super().save(*args, **kwargs)


    @property
    def occupants_num(self):
        # 实时统计这个订单下绑定的入住人数量
        return self.occupants.count()


def __str__(self):
    return f"订单ID: {self. order_id}, 状态: {self.order_status}"
