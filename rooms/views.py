from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render

from rooms.models import *


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
            except Exception as e:
                messages.error(request, {e})
                print(e)

    context = {
        'active_page': 'room',  # 当前页面标识
        'active_function': 'add_room_type'
    }
    return render(request, 'rooms/add_room_type.html', context)


def query_room_type(request):
    room_type_list = RoomType.objects.filter(homestay=request.user.homestay_id)

    # 创建分页器，每页显示5条记录
    paginator = Paginator(room_type_list, 5)
    # 从请求中获取页码，默认为第一页
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
            'active_page': 'room',  # 当前页面标识
            'active_function': 'query_room_type',
            'page_obj': page_obj
        }
    return render(request, 'rooms/query_room_type.html', context)
