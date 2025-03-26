import logging
from datetime import datetime, date
from pydoc import pager

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import *
from luxora_utils.list_utils import paginate
from luxora_utils.order_utils import filter_orders, get_available_room_types, create_order
from luxora_utils.permissions import role_required
from orders.models import Order, Occupant
from rooms.models import Room, RoomType

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)
@login_required
@role_required('reception')
def reception(request):
    current_user = request.user
    context = {
        'active_page': 'home',  # 当前页面标识
        "homestay_name": Homestay.objects.get(id=current_user.homestay_id).name,
    }
    return render(request, 'accounts/reception/reception.html', context)


@login_required
@role_required('reception')
def query_check_in(request):
    # search_query_phone = request.GET.get('search_query_phone')
    # search_query_name = request.GET.get('search_query_name')
    # search_query_IDcard = request.GET.get('search_query_IDcard')
    # expected_check_in_time = request.GET.get('expected_check_in_time')
    order_list = Order.objects.filter(order_status='booked',homestay_id=request.user.homestay_id,
                                      # expected_check_in_date=date.today()
                                      )
    order_list = filter_orders(request, order_list)
    page_obj = paginate(request, order_list, 10)



    context = {
        'active_page': 'check_in',  # 当前页面标识
        'page_obj': page_obj,
    }
    return render(request, 'accounts/reception/query_check_in.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('reception'), name='dispatch')
class CheckInView(View):
    """
    办理入住视图（带后端校验）
    """

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        room_list = Room.objects.filter(room_type=order.room_type, room_status='available')
        page = request.GET.get('page', '1')

        context = {
            'active_page': 'check_in',
            'order': order,
            'room_list': room_list,
            'page': page
        }
        return render(request, 'accounts/reception/check_in.html', context)

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        room_list = Room.objects.filter(room_type=order.room_type, room_status='available')
        payment_method = request.POST.get('payment_method', '').split()

        try:
            # 房间校验
            room_id_str = request.POST.get('room_id', '').strip()
            Validator.not_empty(room_id_str, "房间号")
            room_id = int(room_id_str) if room_id_str.isdigit() else None
            room = get_object_or_404(Room, pk=room_id, room_status='available')


            if order.payment_channel == 'in_store':
                Validator.valid_in_choices(payment_method, ["cash", "wechat", "alipay", "bank_transfer"], "支付方式")

            # 入住人校验
            occupant_names = request.POST.getlist("occupant_name[]")
            occupant_id_cards = request.POST.getlist("occupant_id_card[]")
            if not occupant_names or not occupant_id_cards or len(occupant_names) != len(occupant_id_cards):
                raise ValidationError("请至少添加一位入住人，且姓名与身份证数量匹配")

            for name, id_card in zip(occupant_names, occupant_id_cards):
                Validator.not_empty(name, "入住人姓名")
                Validator.valid_id_card(id_card, "入住人身份证")

                # 核心校验：查 Occupant 表，确保身份证存在且对应姓名一致
                try:
                    occupant = Occupant.objects.get(id_card=id_card)
                    if occupant.name != name:
                        raise ValidationError(f"身份证【{id_card}】对应的姓名应为【{occupant.name}】，请检查输入")
                except Occupant.DoesNotExist:
                    raise ValidationError(f"系统中不存在身份证号【{id_card}】的入住人记录，请先添加或核实")




            # 更新订单
            order.room = room
            order.order_status = 'checked_in'
            order.check_in_datetime = datetime.now()
            order.save()

            # 更新房间状态
            room.room_status = 'check_in'
            room.save()

            # 入住人绑定
            for name, id_card in zip(occupant_names, occupant_id_cards):
                occupant, created = Occupant.objects.get_or_create(
                    id_card=id_card,
                    defaults={'name': name}
                )
                order.occupants.add(occupant)

            messages.success(request, f'入住成功，房间号：{room.room_number}')
            page = request.GET.get('page', 1)
            return redirect(f'{reverse("query_check_in")}?page={page}')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'入住失败：{e}')

        # 校验失败，回显
        context = {
            'active_page': 'check_in',
            'order': order,
            'room_list': room_list,
        }
        return render(request, 'accounts/reception/check_in.html', context)

@role_required('reception')
@login_required
def query_check_out(request):
    order_list = Order.objects.filter(order_status='checked_in',
                                      homestay_id=request.user.homestay_id,
                                      # expected_check_out_date=date.today()
                                      )

    order_list = filter_orders(request, order_list)
    page_obj = paginate(request, order_list, 10)

    context = {
        'active_page': 'check_out',  # 当前页面标识
        'page_obj': page_obj,
    }

    return render(request, 'accounts/reception/query_check_out.html', context)


@role_required('reception')
@login_required
def check_out(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    try:
        order.check_out_time = datetime.now()
        order.order_status = 'checked_out'

        room = order.room
        room.room_status = 'cleaning'

        order.save()
        room.save()
        messages.success(request, f'退房成功，订单号 {order.order_id}')
        return redirect(reverse('query_check_out'))
    except Exception as e:
        messages.error(request, f'退房失败，请重试！{e}')
        print(e)
        page = request.GET.get('page', '1')
        return redirect(f'{reverse("query_check_out")}?page={page}')


from django.contrib import messages
from django.core.exceptions import ValidationError
from luxora_utils.validators import Validator  # 你的校验工具类


@role_required('reception')
@login_required
def book(request):
    homestay_id = request.user.homestay_id
    homestay_name = Homestay.objects.get(pk=homestay_id).name

    if request.method == 'POST':
        try:
            # 获取数据
            start_date_str = request.POST.get('expected_check_in_date')
            end_date_str = request.POST.get('expected_check_out_date')
            days = request.POST.get('days')
            type_id = request.POST.get('type_id')
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            customer_IDcard = request.POST.get('customer_IDcard')
            payment_channel = request.POST.get('payment_channel')
            payment_method = request.POST.get('payment_method')

            # 校验开始
            Validator.not_empty(customer_name, "客户姓名")
            Validator.valid_phone(customer_phone)
            Validator.valid_id_card(customer_IDcard)
            days = Validator.valid_positive_int(days, "入住天数")
            start_date = Validator.valid_date(start_date_str, "入住日期")
            end_date = Validator.valid_date(end_date_str, "离店日期")
            if start_date >= end_date:
                raise ValidationError("离店日期必须晚于入住日期")

            Validator.valid_in_choices(payment_channel, ["advance", "in_store"], "支付渠道")
            if payment_channel == "advance":
                Validator.valid_in_choices(payment_method, ["cash", "wechat", "alipay", "bank_transfer"], "支付方式")

            # 校验房型是否存在
            if not RoomType.objects.filter(pk=type_id, homestay_id=homestay_id).exists():
                raise ValidationError("房型不存在")

            # 所有校验通过，组装客户信息
            customer_info = {
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'customer_IDcard': customer_IDcard
            }

            # 调用创建订单
            order = create_order(
                homestay_id, type_id, start_date, days, end_date,
                customer_info, payment_channel, payment_method
            )

            messages.success(request, "下单成功，订单号: {}".format(order.order_id))
            # 可以考虑跳转
            # return redirect('some_success_page')

        except ValidationError as e:
            # 捕获校验异常，前端用 messages.error 提示
            messages.error(request, str(e))
            # 中断流程，直接返回页面（带上错误提示）
            context = {
                'active_page': 'book',
                'homestay_name': homestay_name,
            }
            return render(request, 'accounts/reception/book.html', context)

    # GET请求或正常流程渲染
    context = {
        'active_page': 'book',
        'homestay_name': homestay_name,
    }
    return render(request, 'accounts/reception/book.html', context)




