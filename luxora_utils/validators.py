import re
from datetime import datetime
from django.core.exceptions import ValidationError


class Validator:

    @staticmethod
    def not_empty(value, field_name):
        if not value or str(value).strip() == '':
            raise ValidationError(f"{field_name}不能为空")

    @staticmethod
    def valid_phone(phone, field_name="手机号"):
        if not re.match(r'^\d{11}$', str(phone)):
            raise ValidationError(f"{field_name}格式错误，必须是11位数字")

    @staticmethod
    def valid_id_card(id_card, field_name="身份证"):
        if not re.match(r'^\d{15}$|^\d{18}$|^\d{17}[Xx]$', str(id_card)):
            raise ValidationError(f"{field_name}格式错误，应为15位或18位或17位+X/x")

    @staticmethod
    def valid_date(date_str, field_name="日期"):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            raise ValidationError(f"{field_name}格式错误，正确格式应为 YYYY-MM-DD")

    @staticmethod
    def valid_positive_int(value, field_name="数值"):
        try:
            ivalue = int(value)
            if ivalue <= 0:
                raise ValidationError(f"{field_name}必须大于0")
            return ivalue
        except Exception:
            raise ValidationError(f"{field_name}格式错误，必须是整数")

    @staticmethod
    def valid_in_choices(value, choices, field_name="字段"):
        if value not in choices:
            raise ValidationError(f"{field_name}不合法，必须是 {choices} 之一")

    # 工号校验（只能字母或数字）
    @staticmethod
    def valid_employee_id(emp_id, field_name="工号"):
        if not re.match(r'^[a-zA-Z0-9]+$', emp_id):
            raise ValidationError(f"{field_name}只能由字母和数字组成")

    # 密码校验
    @staticmethod
    def valid_password_strong(password, field_name="密码"):
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
        if not re.match(pattern, password):
            raise ValidationError(f"{field_name}必须至少8位，且包含大小写字母和数字")
