from datetime import datetime, timedelta

from django.db.models import Count
from django.db.models.fields import return_None

from orders.models import Order
from rooms.models import RoomType, Room


# 今日预抵
def get_arrival_count(homestay_id):
    """
    今日预抵
    :param homestay_id:
    :return:
    """
    today = datetime.today().date()
    arrival_count = Order.objects.filter(homestay_id=homestay_id, expected_check_in_date =today).count()
    return arrival_count

# 今日预离
def get_departure_count(homestay_id):
    """
    今日预离
    :param homestay_id:
    :return:
    """
    today = datetime.today().date()
    departure_count = Order.objects.filter(homestay_id=homestay_id, expected_check_out_date =today).count()
    return departure_count

# 已入住
def get_check_in_count(homestay_id):
    """
    已入住
    :param homestay_id:
    :return:
    """
    today = datetime.today().date()
    check_in_count = Order.objects.filter(homestay_id=homestay_id, expected_check_in_date =today, order_status='checked_in').count()
    return check_in_count

# 已退房
def get_check_out_count(homestay_id):
    """
    已退房
    :param homestay_id:
    :return:
    """
    today = datetime.today().date()
    check_out_count = Order.objects.filter(homestay_id=homestay_id, expected_check_out_date =today, order_status='checked_out').count()
    return check_out_count

# 未排房
def get_book_count(homestay_id):
    """
    未排房
    :param homestay_id:
    :return:
    """
    today = datetime.today().date()
    book_count = Order.objects.filter(homestay_id=homestay_id, expected_check_in_date =today, order_status='booked').count()
    return book_count

# 今日新增订单
def get_today_order_count(homestay_id):
    """
    今日新增订单
    :param homestay_id:
    :return:
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    today_order_count = Order.objects.filter(
        homestay_id=homestay_id,
        created_at__gte=today,  # 大于等于今天 00:00:00
        created_at__lt=tomorrow # 小于今天 00:00:00
    ).exclude(order_status='cancelled').count()
    return today_order_count


# 近7天入住率
def get_check_in_rate(homestay_id):
    """
    计算近7天每天的入住率，排除已取消的订单
    """
    total_rooms = Room.objects.filter(room_type__homestay_id=homestay_id).count() or 1

    date_list = []
    occupancy_list = []

    for i in range(6, -1, -1):  # 最近7天
        day = datetime.now().date() - timedelta(days=i)
        date_list.append(day.strftime("%m-%d"))

        # 核心：排除取消订单

        active_orders = Order.objects.filter(
            homestay_id=homestay_id,  # 限制只统计当前民宿下的订单
            expected_check_in_date__lte=day,  # 订单入住日期 <= 当前统计的这一天
            expected_check_out_date__gt=day  # 订单退房日期 > 当前统计的这一天（当天仍在住）
        ).exclude(order_status='cancelled').count()  # 排除状态为取消的订单

        occupancy_rate = round(active_orders / total_rooms, 2)
        occupancy_list.append(occupancy_rate)

        # 打印这天有多少有效单
        # print(f"[{day}] 统计结果 -> 有效订单数：{active_orders} / 总房间数：{total_rooms}")

    return date_list, occupancy_list
