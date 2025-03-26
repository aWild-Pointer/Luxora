import calendar
import logging
from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from luxora_utils.list_utils import paginate
from orders.models import Order
from rooms.models import *


# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)



# 新增房型
@login_required
def add_room_type(request):
    if request.method == 'POST':
        type_name = request.POST['type_name']
        capacity = request.POST['capacity']
        base_price = request.POST['base_price']
        introduction = request.POST['introduction']
        homestay = request.user.homestay
        extra_price = request.POST['extra_price']
        expected_check_in = request.POST['expected_check_in']
        expected_check_out = request.POST['expected_check_out']
        print(type_name, capacity, base_price, introduction, homestay)
        if RoomType.objects.filter(type_name=type_name).exists():
            messages.error(request, '该房型已存在')
        else:
            try:
                new_RoomType = RoomType.objects.create(type_name=type_name, capacity=capacity,
                                                       base_price=base_price, introduction=introduction,
                                                       homestay=homestay, extra_price=extra_price,
                                                       expected_check_in=expected_check_in,expected_check_out=expected_check_out)
                messages.success(request, f'{new_RoomType.type_name} 已成功添加')
                logger.info('添加房型成功 (employee_id: %s, type_id: %s, homestay_id: %s, IP:%S)',request.user.employee_id, new_RoomType.type_id, homestay.id, request.ip)
            except Exception as e:
                messages.error(request, f'添加房型失败，原因：{e}')
                logger.error("添加房型失败 (employee_id: %s, homestay_id: %s, IP: %s), 原因：%s",
                                request.user.employee_id, homestay.id, request.ip, e)
                print(e)

    context = {
        'active_page': 'room',  # 当前页面标识
        'active_function': 'add_room_type'
    }
    return render(request, 'rooms/add_room_type.html', context)


# 查询房型
@login_required
def query_room_type(request):
    # 获取 GET 参数（如果没有传入则默认为空字符串）
    search_query = request.GET.get('search_query', '')
    try:
        room_type_list = RoomType.objects.filter(homestay=request.user.homestay_id)
        if search_query:
            room_type_list = room_type_list.filter(type_name__icontains=search_query)
    except Exception as e:
        messages.error(request, f"搜索失败: {str(e)}")
        room_type_list = RoomType.objects.none()


    page_obj = paginate(request, room_type_list, 5)

    context = {
            'active_page': 'room',  # 当前页面标识
            'active_function': 'query_room_type',
            'page_obj': page_obj
        }
    return render(request, 'rooms/query_room_type.html', context)


# 房型信息
def room_type_info(request, type_id):
    room_type = RoomType.objects.get(type_id=type_id)
    page = request.GET.get('page', '1')
    context = {
        'active_page': 'room',  # 当前页面标识
        'active_function': 'query_room_type',
        'room_type': room_type,
        'page': page
    }
    return render(request, 'rooms/room_type_info.html', context)



# 保存房型信息
def edit_room_type_info(request, type_id):
    if request.method == 'POST':
        try:
            room_type = get_object_or_404(RoomType, type_id=type_id)

            old_room_type_data = {
                'type_name': room_type.type_name,
                'capacity': room_type.capacity,
                'base_price': room_type.base_price,
                'extra_price': room_type.extra_price,
                'expected_check_in': room_type.expected_check_in,
                'expected_check_out': room_type.expected_check_out,
                'introduction': room_type.introduction,
            }

            type_name = request.POST.get('type_name', '').strip()
            capacity = request.POST.get('capacity', '2').strip()
            base_price = request.POST.get('base_price', '0.00').strip()
            extra_price = request.POST.get('extra_price', '0.00').strip()
            expected_check_in = request.POST.get('expected_check_in','14:00:00').strip()
            expected_check_out = request.POST.get('expected_check_out','12:00:00').strip()
            introduction = request.POST.get('introduction', '').strip()

            print(type_name, capacity, base_price, introduction)
            # 更新信息
            room_type.type_name = type_name
            room_type.capacity = capacity
            room_type.base_price = base_price
            room_type.extra_price = extra_price
            room_type.expected_check_in = expected_check_in
            room_type.expected_check_out = expected_check_out
            room_type.introduction = introduction

            room_type.save()
            messages.success(request, "房型信息已更新！")
            logger.info('更新房型信息成功 (old: type_id: %s, homestay_id: %s, type_name: %s, capacity: %s,'
                         ' base_price: %s, extra_price: %s, expected_check_in: %s, expected_check_out: %s, introduction: %s, IP:%s)',
                         type_id, request.user.homestay_id, old_room_type_data['type_name'], old_room_type_data['capacity'], old_room_type_data['base_price'],
                         old_room_type_data['extra_price'],old_room_type_data['expected_check_in'],old_room_type_data['expected_check_out'],old_room_type_data['introduction'], request.ip)
        except Exception as e:
            messages.error(request, f"更新失败，原因：{e}")
            logger.error('更新房型信息失败 (type_id: %s, homestay_id: %s, IP: %s), 原因：%s', type_id, request.user.homestay_id, request.ip, e)
        page = request.GET.get('page', '1')
    return redirect(f'{reverse("room_type_info", args=[type_id])}?page={page}')


# 删除房型
@login_required
def delete_room_type(request, type_id):
    try:
        room_type = get_object_or_404(RoomType, type_id=type_id)
        type_name = room_type.type_name
        type_id = room_type.type_id
        room_type.delete()
        messages.error(request, "该房型已删除！")
        logger.info('删除房型成功 (employee_id: %s, type_id: %s, type_name: %s, homestay_id: %s, IP:%s)',request.user.employee_id, type_id, type_name,  request.user.homestay_id, request.ip)
    except Exception as e:
        messages.error(request, f"该房型删除失败，原因：{e}")
        logger.error('删除房型失败 (employee_id: %s, type_id: %s, type_name: %s, homestay_id: %s, IP: %s), 原因：%s',
                      request.user.employee_id, type_id, type_name, request.user.homestay_id, request.ip, e)
    page = request.GET.get('page', '1')
    return redirect(f'{reverse("query_room_type")}?page={page}')



# 查询房间
@login_required
def query_room(request, type_id):
    room_list = Room.objects.filter(room_type=type_id)
    room_type = RoomType.objects.get(type_id=type_id)

    page = request.GET.get('page', '1')
    status_counts = room_type.status_counts
    context = {
        'role': 'rooms/add_room_type.html',
        'active_page': 'room',  # 当前页面标识
        'active_function': 'query_room_type',
        'room_list': room_list,
        'room_type': room_type,
        'page': page,
        'status_counts': status_counts
    }
    return render(request, 'rooms/query_room.html', context)



@login_required
def add_room(request, type_id):
    if request.method == 'POST':
        room_type = get_object_or_404(RoomType, type_id=type_id)
        room_number = request.POST.get('room_number', '').strip()
        room_status = request.POST.get('room_status', '').strip()
        try:
            room = Room.objects.create(room_number=room_number, room_type=room_type, room_status=room_status)
            messages.success(request, "房间已添加！")
            logger.info('添加房间成功 (room_id: %s, room_type: %s, status: %s, homestay_id: %s, IP:%s)',
                         room_number, room_type, room_status, request.user.homestay_id, request.ip)
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("query_room", args=[type_id])}?page={page}')
        except Exception as e:
            messages.error(request, f"添加失败，原因：{e}")
            logger.error('添加房间失败 (room_id: %s, room_type: %s, status: %s, homestay_id: %s, IP: %s), 原因：%s',
                          room_number, room_type, room_status, request.user.homestay_id, request.ip, e)
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("query_room", args=[type_id])}?page={page}')




def room_type_overview(request):
    homestay_id = request.user.homestay_id
    today = datetime.now().date()

    # 时间区间：前7天 ~ 后14天
    date_range = []
    for i in range(-7, 15):  # 25天窗口
        day = today + timedelta(days=i)
        date_range.append({
            'date_obj': day,
            'date_str': day.strftime("%Y-%m-%d"),  # 2025-03-25 格式
            'weekday_num': day.weekday(),  # 0-6，周一=0，周日=6
            'weekday_str': f"周{'一二三四五六日'[day.weekday()]}",  # 直接生成"周一"
            'is_weekend': True if day.weekday() in [4, 5] else False  # 周五/周六标记True

        })

    # 取出所有房型
    room_types = RoomType.objects.filter(homestay_id=homestay_id)
    # 房型表
    calendar_data = []

    for room_type in room_types:
        room_total = room_type.remaining
        daily_status = []

        for day in date_range:
            occupied_count = Order.objects.filter(
                homestay_id=homestay_id,
                room_type=room_type.type_id,
                expected_check_in_date__lte=day['date_obj'],
                expected_check_out_date__gt=day['date_obj'],
                order_status__in=['booked', 'checked_in']
            ).count()

            remaining = max(room_total - occupied_count, 0)
            daily_status.append({
                'occupied': occupied_count, # 当天被占用的数量
                'remaining': remaining  # 当天剩余的数量
            })

        calendar_data.append({
            'room_type': room_type.type_name,
            'room_total': room_total,
            'daily_status': daily_status    # 当前房型的每日房态
        })

    # 日期范围字符串
    start_date_str = date_range[0]['date_obj'].strftime("%Y-%m-%d")
    end_date_str = date_range[-1]['date_obj'].strftime("%Y-%m-%d")

    context = {
        'active_page': 'room',
        'active_function':'room_type_overview',
        'calendar_data': calendar_data,
        'date_range': date_range,
        'today': datetime.now().strftime("%Y-%m-%d"),
        'date_range_str': f"{start_date_str} ~ {end_date_str}",
    }

    print(context)
    return render(request, 'rooms/room_type_overview.html', context)

def update_room(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)

    if request.method == 'POST':
        room_status = request.POST.get('modal_room_status', '').strip()
        print('room_status:', room_status)

        try:
            room.room_status = room_status
            room.save()
            messages.success(request, '修改成功')
        except Exception as e:
            messages.error(request, f'修改失败：{e}')

    # GET fallback跳回去
    page = request.GET.get('page', '1')
    type_id = room.room_type.type_id
    return redirect(f'{reverse("query_room", args=[type_id])}?page={page}')