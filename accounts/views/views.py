import logging
from datetime import datetime

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET

from accounts.models import Employee, Homestay
from luxora_utils.order_utils import is_weekend, get_available_room_types

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


# 登录视图
def login_view(request):

    if request.method == 'POST':
        homestay_id = request.POST.get('homestay', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        password = request.POST.get('password', '').strip()
        print(homestay_id, employee_id, password)

        # 从数据库中获取用户
        try:
            user = Employee.objects.get(homestay_id=homestay_id, employee_id=employee_id)
            # 调试信息：输出角色、输入密码和存储的密码哈希
            # print(user.role, password, user.password)
            # print(check_password(password, user.password))

            # 验证密码
            if check_password(password, user.password):
                if not user.is_active:
                    messages.error(request, '该账户已被禁用！')
                    logger.warning("登录失败：账户禁用 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id, request.ip)
                    return render(request, 'accounts/login.html')
                # 登录成功，保存用户到 session
                login(request, user)
                logger.info("登录成功 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id, request.ip)
                # 根据用户角色重定向（确保 user.role 对应一个合法的 URL 或 URL 名称）
                return redirect(user.role)
            else:
                messages.error(request, '密码错误！')
                logger.warning("登录失败：密码错误 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id,request.ip)
                return render(request, 'accounts/login.html')
        except Employee.DoesNotExist:
            messages.error(request, '工号或民宿号错误！')
            logger.warning("登录失败：用户不存在 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id, request.ip)
            return render(request, 'accounts/login.html')

    # GET 请求，直接渲染登录页面
    return render(request, 'accounts/login.html')


# 注册视图
def register_view(request):
    new_employee = None
    if request.method == 'POST':
        homestay_id = request.POST.get('id', '').strip()
        homestay_name = request.POST.get('name', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        employee_name = request.POST.get('employee_name', '').strip()
        role = request.POST.get('role', '').strip()
        # password = request.POST.get('user_password', '').strip()
        print(employee_id, employee_name, role)

        homestay, created = Homestay.objects.get_or_create(
            id=homestay_id,
            defaults={'name': homestay_name},  # 如果民宿不存在，则使用提供的名称创建
        )
        if created:
            logger.info("系统创建民宿 (homestay_id: %s, name: %s, IP: %s)", homestay_id, homestay_name, request.ip)

        if not created and homestay.name != homestay_name:
            messages.error(request, "当前民宿号与民宿名称不符!")
            return render(request, 'accounts/register.html')

        # print(homestay.id,Employee.objects.get(employee_id=employee_id).homestay_id)
        # 检查用户 ID 是否已存在
        if Employee.objects.filter(employee_id=employee_id, homestay_id=homestay.id).exists():
            messages.error(request, "用户工号已存在，请更换!")
            return render(request, 'accounts/register.html')
        else:
            try:
                new_employee = Employee.objects.create(
                    employee_id=employee_id,
                    username=homestay_id + '_' + employee_id + '_' + employee_name,
                    employee_name=employee_name,
                    # 明文
                    employee_password='123456',
                    # 加密
                    password=make_password('123456'),
                    role=role,
                    homestay=homestay
                )
                messages.success(request, '员工账号注册成功！')
                logger.info("注册员工账号成功 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id, request.ip)
            except Exception as e:
                messages.error(request, f'创建失败，原因：{e}')
                logger.error("注册创建员工账号失败 (employee_id: %s, homestay_id: %s, IP: %s), 原因：%s", employee_id, homestay_id, request.ip, e)
                print(e)

    return render(request, 'accounts/register.html', {"new_employee": new_employee})
    # return render(request, 'test.html', {"new_employee": new_employee})


# 登出视图
@login_required
@require_GET
def logout_view(request):
    employee_id, homestay_id = None, None
    try:
        employee_id = request.user.employee_id
        homestay_id = request.user.homestay_id
        logout(request)
        messages.success(request, '您已成功退出登录！')
        logger.info("登出成功 (employee_id: %s, homestay_id: %s, IP: %s)", employee_id, homestay_id, request.ip)
    except Exception as e:
        messages.error(request, f'登出失败，原因：{e}')
        logger.error("登出失败 (employee_id: %s, homestay_id: %s, IP: %s), 原因：%s", employee_id, homestay_id, request.ip, e)
    return redirect('login')








# 员工修改个人信息
@login_required
def update_self_info(request):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=request.user.id)
            old_employee_data = employee.get_info()

            employee_name = request.POST.get('employee_name', '').strip()
            employee_phone = request.POST.get('employee_phone', '').strip()
            employee_IDcard = request.POST.get('employee_IDcard', '').strip()
            employee_address = request.POST.get('employee_address', '').strip()
            print(employee_name, employee_phone, employee_IDcard, employee_address)

            employee.update_info(employee_name=employee_name,employee_phone=employee_phone,
                                 employee_IDcard=employee_IDcard,employee_address=employee_address,)
                                 # employee_password = employee_password, password = employee_password)
            messages.success(request, '保存成功！')
            logger.info("员工(employee_id: %s, homestay_id: %s, IP: %s) 修改个人信息成功 (old: employee_name: %s, employee_phone: %s, employee_IDcard: %s, employee_address: %s)",
                        employee.employee_id, employee.homestay_id, request.ip, old_employee_data['employee_name'], old_employee_data['employee_phone'],
                        old_employee_data['employee_IDcard'], old_employee_data['employee_address'])
        except Exception as e:
            messages.error(request, '保存失败，请重试！')
            logger.error("员工(employee_id: %s, homestay_id: %s, IP: %s) 修改个人信息失败, 原因：%s", request.user.employee_id, request.user.homestay_id, request.ip, e)
            # 返回上一个页面
        return redirect(request.META.get('HTTP_REFERER', reverse(f'{request.user.role}')))  # 如果没有 Referer，则回到首页
        # return redirect(reverse(f'{employee.role}'))  # 如果没有 Referer，则回到首页


# 修改密码
@login_required
def update_password(request):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=request.user.id)
            old_password = request.POST.get('old_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            if employee.check_password(old_password):
                if new_password != confirm_password:
                    messages.error(request, "两次输入的密码不一致！")
                    return redirect(request.META.get('HTTP_REFERER', reverse(f'{request.user.role}')))  # 如果没有 Referer，则回到首页
                if old_password == new_password:
                    messages.error(request, "新密码不能与旧密码相同！")
                    return redirect(request.META.get('HTTP_REFERER', reverse(f'{request.user.role}')))  # 如果没有 Referer，则回到首页
                employee.set_password(new_password)
                print(new_password, employee.password)
                employee.employee_password = new_password
                employee.save()
                # 更新会话的认证哈希，防止修改密码后用户被登出
                update_session_auth_hash(request, employee)
                messages.success(request, '修改密码成功！')
                logger.info("员工(employee_id: %s, homestay_id: %s, IP: %s) 修改密码成功", employee.employee_id, employee.homestay_id, request.ip)
            else:
                messages.error(request, '密码错误，请重试！')
        except Exception as e:
            messages.error(request, '修改密码失败，请重试！')
            logger.error("员工(employee_id: %s, homestay_id: %s, IP: %s) 修改密码失败, 原因：%s", request.user.employee_id, request.user.homestay_id, request.ip, e)
            # 返回上一个页面
    return redirect(request.META.get('HTTP_REFERER', reverse(f'{request.user.role}')))  # 如果没有 Referer，则回到首页



# 重置密码
@login_required
def reset_password(request, id):
    try:
        employee = Employee.objects.get(id=id)
        employee.set_password('123456')
        employee.employee_password = '123456'
        employee.save()
        messages.success(request, '重置密码成功！')

        if request.user.id == employee.id:
            # 更新会话的认证哈希，防止修改密码后用户被登出
            update_session_auth_hash(request, employee)

        logger.info("员工(employee_id: %s, homestay_id: %s, IP: %s) 重置密码成功", employee.employee_id, employee.homestay_id, request.ip)
    except Exception as e:
        messages.error(request, '重置密码失败，请重试！')
    page = request.GET.get('page', '1')
    # 返回拼接url
    return redirect(f'{reverse("manager_query_employee")}?page={page}')


# 测试视图
def test_view(request):
    messages.info(request, "消息测试!")
    messages.error(request, "错误测试!")
    messages.success(request, "成功测试!")
    context = {
        "is_weekend": is_weekend(),  # 传递是否为周末的布尔值
    }

    statr_date = datetime.strptime('2025-1-1', "%Y-%m-%d").date()
    end_date = datetime.strptime('2025-1-2', "%Y-%m-%d").date()
    list = get_available_room_types(request.user.homestay_id, statr_date,end_date)
    print(list)
    return render(request, 'test.html', context)
