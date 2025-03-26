# 民宿管理员模板
import random
from datetime import timedelta

from django.contrib.auth.decorators import login_required
import logging

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET

from luxora_utils.list_utils import paginate
from luxora_utils.permissions import role_required
from luxora_utils.statistic_utils import *
from accounts.models import Employee, Homestay
from luxora_utils.validators import Validator

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

@login_required
@role_required('manager')
def manager(request):
    current_user = request.user

    arrival_count = get_arrival_count(current_user.homestay_id)
    departure_count = get_departure_count(current_user.homestay_id)
    check_in_count = get_check_in_count(current_user.homestay_id)
    check_out_count = get_check_out_count(current_user.homestay_id)
    book_count = get_book_count(current_user.homestay_id)
    today_order_count = get_today_order_count(current_user.homestay_id)

    date_list, occupancy_list = get_check_in_rate(current_user.homestay_id)

    context = {
        'active_page': 'home',  # 当前页面标识
        "homestay_name": Homestay.objects.get(id=current_user.homestay_id).name,
        'arrival_count': arrival_count,
        'departure_count': departure_count,
        'check_in_count': check_in_count,
        'check_out_count': check_out_count,
        'book_count': book_count,
        'today_order_count': today_order_count,
        'date_list': date_list,
        'occupancy_list': occupancy_list,

    }
    return render(request, 'accounts/manager/manager.html', context)


# 新增员工视图
@login_required
@role_required('manager')
def add_employee(request):
    try:
        current_user = request.user
        homestay = current_user.homestay
    except Exception:
        messages.error(request, "当前用户没有关联的员工信息!")
        return render(request, 'accounts/manager/manager_add_employee.html')

    if request.method == 'POST':
        employee_id = request.POST.get('id', '').strip()
        employee_name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()

        try:
            # 所有校验直接调用工具类
            Validator.not_empty(employee_id, "工号")
            Validator.valid_employee_id(employee_id)

            Validator.not_empty(employee_name, "姓名")
            Validator.not_empty(password, "密码")
            Validator.valid_password_strong(password)

            Validator.not_empty(role, "角色")

            # 工号唯一性校验
            if Employee.objects.filter(employee_id=employee_id, homestay_id=homestay.id).exists():
                raise ValidationError("用户工号已存在，请更换！")

            # 创建员工
            new_employee = Employee.objects.create(
                employee_id=employee_id,
                username=f"{homestay.id}_{employee_id}_{employee_name}",
                employee_name=employee_name,
                employee_password=password,
                password=make_password(password),
                role=role,
                homestay=homestay
            )

            messages.success(request, f"{new_employee.employee_name} 员工账号创建成功")
            logger.info("民宿管理员(employee_id: %s) 创建员工成功 (employee_id: %s)", current_user.employee_id, employee_id)
            return redirect('manager_employee_list')  # 成功跳转

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error("民宿管理员(employee_id: %s) 创建员工失败 (employee_id: %s), 原因：%s",
                         current_user.employee_id, employee_id, e)
            messages.error(request, "创建员工账号失败，请联系管理员")

    context = {
        'active_page': 'employee',
        'active_function': 'add_employee'
    }
    return render(request, 'accounts/manager/manager_add_employee.html', context)

# 员工详情
@login_required
@role_required('manager')
def employee_info(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    page = request.GET.get('page', '1')
    context = {
        'active_page': 'employee',  # 当前页面标识
        'active_function': 'query_employee',
        'employee': employee,
        'page': page
    }
    return render(request, 'accounts/manager/manager_employee_info.html', context)


# manager修改员工信息
@login_required
@role_required('manager')
def update_employee_info(request, id):
    employee = get_object_or_404(Employee, id=id)
    old_employee_data = employee.get_info()

    if request.method == 'POST':
        try:
            employee_name = request.POST.get('employee_name', '').strip()
            role = request.POST.get('role', '').strip()
            new_employee_id = request.POST.get('employee_id', '').strip()
            employee_phone = request.POST.get('employee_phone', '').strip()
            employee_IDcard = request.POST.get('employee_IDcard', '').strip()
            employee_address = request.POST.get('employee_address', '').strip()

            # 后端校验（字段非空、格式检查）
            Validator.not_empty(employee_name, "员工姓名")
            Validator.not_empty(role, "角色")
            Validator.not_empty(new_employee_id, "工号")
            Validator.valid_employee_id(new_employee_id)

            if employee_phone:
                Validator.valid_phone(employee_phone)
            if employee_IDcard:
                Validator.valid_id_card(employee_IDcard)

            # # 工号唯一性校验（排除当前自己）
            # if (Employee.objects.filter(employee_id=new_employee_id, homestay=employee.homestay)
            #         .exclude(id=employee.id).exists()):

            # 检查新工号是否已存在
            if (Employee.objects.filter(employee_id=new_employee_id, homestay=employee.homestay).exists()
                    and (new_employee_id != employee.employee_id)):
                raise ValidationError("保存失败，工号已存在！")

            # 更新员工信息
            employee.update_info(
                employee_name=employee_name,
                role=role,
                employee_id=new_employee_id,
                employee_phone=employee_phone,
                employee_IDcard=employee_IDcard,
                employee_address=employee_address
            )

            messages.success(request, '保存成功！')
            logger.info("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 修改员工信息成功 (old: %s)",
                        request.user.employee_id, employee.homestay_id, request.ip, old_employee_data)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'保存失败，原因：{e}')
            logger.error("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 修改员工信息失败 (employee_id: %s), 原因：%s",
                         request.user.employee_id, employee.homestay_id, request.ip, employee.employee_id, e)

    page = request.GET.get('page', '1')
    return redirect(f'{reverse("manager_employee_info", args=[id])}?page={page}')




# 员工列表视图
@login_required
@role_required('manager')
def manager_query_employee (request):
    # 获取 GET 参数（如果没有传入则默认为空字符串）
    search_query = request.GET.get('search_query', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')

    try:
        # 初始查询集：所有员工
        employee_list = Employee.objects.filter(homestay_id=request.user.homestay_id, is_delete=False)

        # 根据搜索关键词过滤：对工号或姓名进行模糊搜索
        if search_query:
            employee_list = employee_list.filter(
                # 使用 Q 对象实现多个条件的联合过滤
                Q(employee_id__icontains=search_query) |
                Q(employee_name__icontains=search_query)
            )

        # 根据角色进行过滤
        if role:
            employee_list = employee_list.filter(role=role)

        # 根据状态过滤（GET参数传入的是字符串 "True" 或 "False"）
        if status == "True":
            employee_list = employee_list.filter(is_active=True)
        elif status == "False":
            employee_list = employee_list.filter(is_active=False)
    except Exception as e:
        messages.error(request, f"搜索失败: {str(e)}")
        employee_list = Employee.objects.none()


    page_obj = paginate(request, employee_list, 5)

    context = {
        'active_page': 'employee',  # 当前页面标识
        'active_function': 'query_employee',
        'page_obj': page_obj
    }

    return render(request, 'accounts/manager/manager_query_employee.html', context)


# 账户状态设置视图
@login_required
@role_required('manager')
def set_is_active(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    # 将员工账户设置为禁用或启用状态
    if employee.is_active:
        employee.is_active = False
        messages.info(request, "该账户已成功禁用！")
        logger.info("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 禁用员工账号成功 (employee_id: %s)", request.user.employee_id, employee.homestay_id, request.ip, employee.employee_id)
    else:
        employee.is_active = True
        messages.info(request, "该账户已成功启用！")
        logger.info("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 启用员工账号成功 (employee_id: %s)", request.user.employee_id, employee.homestay_id, request.ip, employee.employee_id)
    employee.save()

    page = request.GET.get('page', '1')
    # 返回拼接url
    return redirect(f'{reverse("manager_query_employee")}?page={page}')


# 注销账户视图
@login_required
@role_required('manager')
def delete_employee(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    try:
        # employee.delete()
        employee.is_delete = True
        employee.save()
        messages.info(request, "该账户已注销！")
        logger.info("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 注销员工账号成功 (employee_id: %s)", request.user.employee_id, employee.homestay_id, request.ip, employee.employee_id)
    except Exception as e:
        messages.error(request, '该账户注销失败，请重试！')
        logger.error("民宿管理员(employee_id: %s, homestay_id: %s, IP: %s) 注销员工账号失败 (employee_id: %s), 原因：%s", request.user.employee_id, employee.homestay_id, request.ip, employee.employee_id, e)

    page = request.GET.get('page', '1')
    # 返回拼接url
    return redirect(f'{reverse("manager_query_employee")}?page={page}')
