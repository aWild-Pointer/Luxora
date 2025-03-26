from django.contrib.messages import success
from django.db import transaction
from django.db.models import Q, Count
from datetime import datetime, date, timedelta
from django.contrib import messages

from orders.models import Order
from rooms.models import RoomType


def filter_orders(request, queryset):
    """
    通用订单查询函数
    :param request: Django request 对象
    :param queryset: 订单的 QuerySet，如 Order.objects.all()
    :return: 过滤后的 QuerySet（支持分页）
    """

    # 先过滤掉非当前用户所属的订单
    queryset = queryset.filter(homestay_id=request.user.homestay_id)

    # 单独处理搜索关键字（多字段模糊）
    search_query = request.GET.get("search_query", "").strip()
    if search_query:
        queryset = queryset.filter(
            Q(order_id__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_IDcard__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )

    # 定义查询规则
    filters = {
        "order_id": ("order_id__icontains", str),  # 订单号模糊搜索
        "customer_name": ("customer_name__icontains", str),  # 按客户姓名查询
        "customer_IDcard": ("customer_IDcard__icontains", str),  # 按身份证查询
        "customer_phone": ("customer_phone__icontains", str),  # 按手机号查询
        "order_status": ("order_status", str),  # 精确匹配订单状态
        "expected_check_in_date": ("expected_check_in_date", "date"),  # 入住日期
        "expected_check_out_date": ("expected_check_out_date", "date"),  # 离店日期
    }

    try:
        # 遍历 `filters` 进行查询
        for param, (field, field_type) in filters.items():
            value = request.GET.get(param, "").strip()
            if value:
                if field_type == "date":
                    value = datetime.strptime(value, "%Y-%m-%d").date()  # 转换日期格式
                queryset = queryset.filter(**{field: value})  # 过滤查询
    except Exception as e:
        messages.error(request, f"查询失败：{str(e)}")
        queryset = queryset.none()

    return queryset

# 周末入住
def is_weekend():
    """
    判断今天是否是周末（周六或周日）
    """
    today = date.today()
    return today.weekday() in [4, 5]  # 5=周六, 6=周日

# 查询可用房型
def get_available_room_types(homestay_id, start_date, end_date):
    """
    返回该民宿下在指定日期区间还有空房的房型列表。
    """

    # 找出在该区间内处于已预订/已入住状态的订单（按房型分组统计）
    occupied = (Order.objects
        .filter(
            homestay_id=homestay_id,
            order_status__in=['booked', 'checked_in'],
            expected_check_in_date__lt=end_date,
            expected_check_out_date__gt=start_date
        )
        .values('room_type')  # 按房型
        .annotate(count_orders=Count('order_id'))  # 每个房型已有多少订单(简单起见: 每笔订单占1间)
    )

    # 做成字典 {room_type_id: 占用数}
    occupied_dict = {item['room_type']: item['count_orders'] for item in occupied}

    # 取出所有房型
    all_room_types = RoomType.objects.filter(homestay_id=homestay_id)

    available_rt = []
    for rt in all_room_types:
        # rt.remaining 表示此房型总房数
        # used = occupied_dict.get(rt.type_id, 0)
        # if used < rt.remaining:
        #     available_rt.append(rt)
        used = occupied_dict.get(rt.type_id, 0)
        # 计算剩余可订数
        remain = rt.remaining - used
        if remain > 0:
            # 直接加上余量信息
            available_rt.append({
                'room_type': rt,
                'remaining': remain
            })

    return available_rt

# 新建订单
@transaction.atomic
def create_order(homestay_id, type_id, start_date, days,
                 end_date, customer_info, payment_channel, payment_method):
    # 1) 加行级锁获取此房型
    room_type = RoomType.objects.select_for_update().get(pk=type_id, homestay_id=homestay_id)

    # 2) 再次检查在 [start_date, end_date) 里, 该房型已占用量
    used_count = (Order.objects
                     .filter(
                         homestay_id=homestay_id,
                         room_type_id=type_id,
                         order_status__in=['booked', 'checked_in'],
                         expected_check_in_date__lt=end_date,
                         expected_check_out_date__gt=start_date
                     )
                     .count()
                 )
    # 如果 used_count >= room_type.remaining，说明没有余量
    if used_count >= room_type.remaining:
        raise ValueError("该房型在所选时间段已售完")

    is_pay = False
    payment_time = None
    if payment_channel == 'online' or payment_channel == 'advance':
        is_pay = True
        payment_time = datetime.now()

    room_type = RoomType.objects.get(pk=type_id)
    # 3) 创建订单 (房间room字段先不填)
    order = Order.objects.create(
        homestay_id=homestay_id,
        room_type=room_type,
        order_status='booked',

        customer_name=customer_info['customer_name'],
        customer_phone=customer_info['customer_phone'],
        customer_IDcard=customer_info['customer_IDcard'],

        expected_check_in_date=start_date,
        expected_check_out_date=end_date,
        days=days,
        expected_check_in_time=room_type.expected_check_in,
        expected_check_out_time=room_type.expected_check_out,

        payment_channel=payment_channel,
        payment_method=payment_method,

        amounts=calculate_price(start_date, room_type, days),
        is_pay=is_pay,
        payment_time=payment_time,
        # 这里 occupant_count, amounts, is_pay等字段也可赋值
    )

    return order

def calculate_price(expected_check_in_date, room_type, days):
    """
    根据入住日期范围和房型，计算总价格
    - 平日价格：room_type.weekday_price
    - 周末价格（周五、周六）：room_type.weekend_price
    """
    print(expected_check_in_date, room_type, days)
    total_price = 0
    current_date = expected_check_in_date

    for i in range(days):
        # 判断是否为周末（周五=4、周六=5）
        if current_date.weekday() in [4, 5]:
            total_price += room_type.weekend_price
        else:
            total_price += room_type.weekday_price
        current_date += timedelta(days=1)

    return total_price
