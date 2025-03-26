from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.contrib.auth.password_validation import password_changed
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

    employee_id = models.CharField(max_length=30, default="default", verbose_name='工号')

    employee_name = models.CharField(max_length=30, default="default", verbose_name='姓名')

    employee_password = models.CharField(max_length=50, default="default", verbose_name='明文密码')

    employee_address = models.CharField(max_length=200, default="default", verbose_name='通讯地址')

    employee_phone = models.CharField(max_length=15, default="default", verbose_name='电话')

    employee_IDcard = models.CharField(max_length=20, default="default", verbose_name='身份证')

    is_delete = models.BooleanField(default=False, verbose_name='是否注销')

    employee_avatar = models.ImageField(upload_to='employee_avatar/', default='user_avatar.jpg', verbose_name='头像')

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

    # 返回员工信息
    def get_info(self):
        employee_data = {
            'employee_name': self.employee_name,
            'role': self.role,
            'employee_id': self.employee_id,
            'employee_phone': self.employee_phone,
            'employee_IDcard': self.employee_IDcard,
            'employee_address': self.employee_address,
        }
        return employee_data

    def update_info(self, **kwargs):
        allowed_fields = {'employee_id', 'employee_name', 'role', 'employee_phone', 'employee_IDcard',
                          'employee_address'}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(self, field, value)
        self.save()

    # def save(self, *args, **kwargs):
    #     # 明文密码，方便测试，仅供生产环境使用
    #     if self.password:
    #         self.employee_password = self.password
    #     else:
    #         self.employee_password = None
    #     # 最后显式调用父类方法，以完成 Django 正常的保存流程
    #     super().save(*args, **kwargs)

