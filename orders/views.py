from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from luxora_utils.list_utils import paginate
from luxora_utils.order_utils import filter_orders, is_weekend, get_available_room_types
from orders.models import *
from rooms.models import *


@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            # 获取表单数据
            order_status = request.POST.get("order_status")
            type_id = request.POST.get("type_id")
            room_number = request.POST.get("room_number")

            customer_name = request.POST.get("customer_name")
            customer_id_card = request.POST.get("customer_id_card")
            customer_phone = request.POST.get("customer_phone")

            expected_check_in_time = request.POST.get("expected_check_in_time")
            days = int(request.POST.get("days", 1))
            expected_check_out_time = request.POST.get("expected_check_out_time")
            print(expected_check_in_time, days, expected_check_out_time)

            room_type = RoomType.objects.get(pk=type_id)

            # 解析日期
            check_in_date = datetime.strptime(expected_check_in_time, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(expected_check_out_time, "%Y-%m-%d").date()

            check_in_time = room_type.expected_check_out
            check_out_time = room_type.expected_check_out

            # 组合完整的 datetime
            check_in_datetime = datetime.combine(check_in_date,check_in_time)
            check_out_datetime = datetime.combine(check_out_date, check_out_time)

            # 确保时间带有时区
            check_in_datetime = timezone.make_aware(check_in_datetime)  # 添加时区
            check_out_datetime = timezone.make_aware(check_out_datetime)

            print(check_in_datetime, check_out_datetime)


            # 处理房号（如果选择“随机”分配房间）
            if room_number == "":
                room_number = None  # 让数据库处理随机分配逻辑


            # 创建订单
            order = Order.objects.create(
                order_status=order_status,
                homestay = request.user.homestay,
                room_type=room_type,
                room=Room.objects.get(pk=room_number) if room_number else None,


                customer_name=customer_name,
                customer_IDcard=customer_id_card,
                customer_phone=customer_phone,

                expected_check_in_time=check_in_time,
                expected_check_in_date=check_in_date,
                expected_check_in_datetime=check_in_datetime,

                days=days,
                expected_check_out_time=check_out_time,
                expected_check_out_date=check_out_date,
                expected_check_out_datetime=check_out_datetime,

                is_pay=False,

            )
            if is_weekend():
                order.amounts = order.room_type.weekend_price * order.days
            else:
                order.amounts = order.room_type.weekday_price * order.days
            order.save()

            # 解析入住人信息
            occupant_names = request.POST.getlist("occupant_name[]")  # 获取所有入住人姓名
            occupant_id_cards = request.POST.getlist("occupant_id_card[]")  # 获取所有入住人身份证号
            for name, id_card in zip(occupant_names, occupant_id_cards):
                occupant, created = Occupant.objects.get_or_create(id_card=id_card, name=name)
                order.occupants.add(occupant)
            messages.success(request, "订单创建成功！")




        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    context = {
        'active_page': 'order',  # 当前页面标识
        'active_function': 'create_order',
        'room_types': RoomType.objects.all(),
    }
    return render(request, 'create_order.html',context)

# 获取可用房型
@login_required
def load_room_type(request):
    homestay_id = request.user.homestay_id
    start_date = request.GET.get('expected_check_in_date')
    end_date = request.GET.get('expected_check_out_date')
    # print(homestay_id, start_date, end_date)

    if homestay_id and start_date and end_date:
        # 将字符串日期转换为 date 对象
        query_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        query_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # 查询可用房型
        available_rt = get_available_room_types(homestay_id, query_start_date, query_end_date)
    else:
        available_rt = []

    return render(request, 'fragments/load_rooms.html', {'room_types': available_rt})




@login_required
def query_order(request):
    # 获取 GET 参数（如果没有传入则默认为空字符串）
    # search_query = request.GET.get('search_query', '')
    # order_status = request.GET.get('order_status', '')
    # expected_check_in_time = request.GET.get('expected_check_in_time', '')
    # expected_check_out_time = request.GET.get('expected_check_out_time', '')


    # print(search_query, order_status, expected_check_in_time, expected_check_out_time)
    try:
    #     order_list = Order.objects.filter(homestay_id=request.user.homestay_id)
    #     if search_query:
    #         order_list = order_list.filter(
    #             Q(order_id__icontains=search_query)
    #
    #         )
    #     if order_status:
    #         order_list = order_list.filter(order_status=order_status)
    #
    #     if expected_check_in_time:
    #         expected_check_in_time = datetime.strptime(expected_check_in_time, "%Y-%m-%d").date()
    #         order_list = order_list.filter(expected_check_in_time__gte=expected_check_in_time)
    #
    #     if expected_check_out_time:
    #         expected_check_out_time = datetime.strptime(expected_check_out_time, "%Y-%m-%d").date()
    #         order_list = order_list.filter(expected_check_out_time__lte=expected_check_out_time)

        order_list = Order.objects.filter(homestay_id=request.user.homestay_id)
        order_list = filter_orders(request, order_list)

    except Exception as e:
        messages.error(request, '查询失败，请重试！')
        order_list = Order.objects.none()


    page_obj = paginate(request, order_list, 10)

    context = {
        'active_page': 'order',  # 当前页面标识
        'active_function': 'manage_order',
        'page_obj': page_obj,
    }
    return render(request, 'query_order.html', context)

def cancel_order(request,order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order.order_status = 'cancelled'
        order.save()
        messages.success(request, '订单取消成功！')
    except Order.DoesNotExist:
        messages.error(request, '订单不存在！')
    except Exception as e:
        messages.error(request, '订单取消失败，请重试！')
    page = request.GET.get('page', '1')
    return redirect(f'{reverse("query_order")}?page={page}')


def order_info(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        print(order.occupants_num)
        context = {
            'active_function': 'manage_order',
            'active_page': 'order',
            'order': order,
        }
        return render(request, 'order_info.html', context)
    except Order.DoesNotExist:
        messages.error(request, '订单不存在！')
        return redirect(reverse('query_order'))
