from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models
from django.db.models import Case, When, IntegerField


class Homestay(models.Model):
    id = models.CharField(max_length=30, unique=True, primary_key=True, default="default", verbose_name='民宿号')

    name = models.CharField(max_length=100, default="default", verbose_name='民宿名称')

    address = models.CharField(max_length=200, default="default", verbose_name='地址')

    introduction = models.TextField(blank=True, verbose_name="民宿介绍")


class Employee(AbstractUser):
    ROLE_CHOICES = [
        ('manager', '民宿管理员'),
        ('reception', '民宿前台'),
        ('cleaner', '民宿保洁'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reception', verbose_name='角色')

    employee_id = models.CharField(max_length=30, unique=True, default="default", verbose_name='工号')

    employee_name = models.CharField(max_length=30, default="default", verbose_name='姓名')

    employee_password = models.CharField(max_length=50, default="default", verbose_name='明文密码')

    employee_address = models.CharField(max_length=200, default="default", verbose_name='通讯地址')

    employee_phone = models.CharField(max_length=15, default="default", verbose_name='电话')

    employee_IDcard = models.CharField(max_length=20, default="default", verbose_name='身份证')

    # 外键：关联到民宿
    homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE, related_name="employees", verbose_name='所属民宿')

    class Meta:
        # 通过 Case + When 实现对 role 字段的自定义排序顺序
        ordering = [
            Case(
                When(role='manager', then=0),
                When(role='reception', then=1),
                When(role='cleaner', then=2),
                default=3,
                output_field=IntegerField()
            ),
            'employee_id',  # 第二排序字段
        ]

# class Employee(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # 与 User 关联
#     ROLE_CHOICES = [
#         ('manager', '民宿管理员'),
#         ('reception', '民宿前台 '),
#         ('cleaner', '民宿保洁'),
#     ]
#     employee_id = models.CharField(max_length=30, unique=True, primary_key=True)
#     employee_password = models.CharField(max_length=150, default='123456')
#     employee_name = models.CharField(max_length=100,default="default")
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reception')
#     homestay = models.ForeignKey(Homestay, on_delete=models.CASCADE, null=True)
