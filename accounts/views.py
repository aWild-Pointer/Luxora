import logging

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from .models import Employee, Homestay


# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 登录视图
def login_view(request):
    if request.method == 'POST':
        homestay = request.POST.get('homestay')
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        print(homestay, employee_id, password)

        # 尝试从数据库中获取用户
        try:
            user = Employee.objects.get(homestay_id=homestay, employee_id=employee_id)
            # 调试信息：输出角色、输入密码和存储的密码哈希
            # print(user.role, password, user.password)
            # print(check_password(password, user.password))

            # 验证密码
            if check_password(password, user.password):
                if not user.is_active:
                    messages.error(request, '该账户已被禁用！')
                    logger.warning("登录失败：账户被禁用 (employee_id: %s, homestay: %s)", employee_id, homestay)
                    return render(request, 'accounts/login.html')
                # 登录成功，保存用户到 session
                login(request, user)
                logger.info("登录成功 (employee_id: %s, homestay: %s)", employee_id, homestay)
                # 根据用户角色重定向（确保 user.role 对应一个合法的 URL 或 URL 名称）
                return redirect(user.role)
            else:
                messages.error(request, '密码错误！')
                logger.warning("登录失败：密码错误 (employee_id: %s, homestay: %s)", employee_id, homestay)
                return render(request, 'accounts/login.html')
        except Employee.DoesNotExist:
            messages.error(request, '工号或民宿号错误！')
            logger.warning("登录失败：用户不存在 (employee_id: %s, homestay: %s)", employee_id, homestay)
            return render(request, 'accounts/login.html')

    # GET 请求，直接渲染登录页面
    return render(request, 'accounts/login.html')


# 注册视图
def register_view(request):
    new_employee = None
    if request.method == 'POST':
        homestay_id = request.POST.get('id')
        homestay_name = request.POST.get('name')
        employee_id = request.POST.get('employee_id')
        employee_name = request.POST.get('employee_name')
        role = request.POST.get('role')
        password = request.POST.get('user_password')
        print(employee_id, employee_name, password, role)

        homestay, created = Homestay.objects.get_or_create(
            id=homestay_id,
            defaults={'name': homestay_name}  # 如果民宿不存在，则使用提供的名称创建
        )
        if not created and homestay.name != homestay_name:
            messages.error(request, "当前民宿号与民宿名称不符!")
            return render(request, 'accounts/register.html')

        # print(homestay.id,Employee.objects.get(employee_id=employee_id).homestay_id)
        # 检查用户 ID 是否已存在
        if Employee.objects.filter(employee_id=employee_id, homestay_id=homestay.id).exists():
            messages.error(request, "用户工号已存在，请更换!")
            return render(request, 'accounts/register.html')
        else:
            new_employee = Employee.objects.create(
                employee_id=employee_id,
                username=homestay_id + '_' + employee_id + '_' + employee_name,
                employee_name=employee_name,
                # 明文
                employee_password=password,
                # 加密
                password=make_password(password),
                role=role,
                homestay=homestay
            )
            messages.success(request, '员工账号创建成功！')

    return render(request, 'accounts/register.html', {"new_employee": new_employee})
    # return render(request, 'test.html', {"new_employee": new_employee})


# 民宿管理员视图
def manager(request):
    current_user = request.user
    context = {
        'active_page': 'home',  # 当前页面标识
        "homestay_name": Homestay.objects.get(id=current_user.homestay_id).name,
    }
    print(context)
    return render(request, 'accounts/manager/manager.html', context)


# 新增员工视图
def add_employee(request):
    # 获取当前登录用户的 Homestay
    current_user = request.user
    print(current_user)
    try:
        # 获取当前用户关联的 Employee 实例
        # employee = Employee.objects.get(id=current_user.id)
        # homestay = employee.homestay  # 获取与当前员工关联的 Homestay
        print(current_user.homestay)
        homestay = current_user.homestay
        # print(homestay.id)
    except Employee.DoesNotExist:
        # homestay = Homestay.objects.get(id='123')  # 获取与当前员工关联的 Homestay
        messages.error(request, "当前用户没有关联的员工信息!")
        return render(request, 'accounts/manager/manager_add_employee.html')

    if request.method == 'POST':
        employee_id = request.POST.get('id', '').strip()
        employee_name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()

        print(employee_id, employee_name, password, role, homestay)

        # 输入校验
        if not id or not employee_name or not password or not role:
            messages.error(request, "所有字段均不能为空!")
            return render(request, 'accounts/manager/manager_add_employee.html')

        # 检查 ID 是否已存在
        if Employee.objects.filter(employee_id=employee_id, homestay_id=homestay.id).exists():
            messages.error(request, "用户工号已存在，请更换!")
            return render(request, 'accounts/manager/manager_add_employee.html')

        # 创建员工
        try:
            new_employee = Employee.objects.create(
                employee_id=employee_id,
                username=homestay.id + '_' + employee_id + '_' + employee_name,
                employee_name=employee_name,
                employee_password=password,
                password=make_password(password),
                role=role,
                homestay=homestay)
            print(new_employee.id)
            messages.success(request, str(new_employee.employee_name) + '员工账号创建成功')
        except Exception as e:
            # messages.error(request, f"添加员工失败: {str(e)}")
            messages.error(request, f"添加员工失败!")
    context = {
        'active_page': 'employee',  # 当前页面标识
        'active_function': 'add_employee'

    }
    return render(request, 'accounts/manager/manager_add_employee.html', context)


# 员工详情
def employee_info(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    page = request.GET.get('page', '1')
    context = {
        'active_page': 'employee',  # 当前页面标识
        'active_function': 'edit_employee',
        'employee': employee,
        'page': page
    }
    return render(request, 'accounts/manager/manager_employee_info.html', context)


# 员工信息修改
def edit_employee(request, id):
    employee = Employee.objects.get(id=id)
    print(employee)
    if request.method == 'POST':
        try:
            employee_name = request.POST.get('employee_name', '').strip()
            role = request.POST.get('role', '').strip()
            new_employee_id = request.POST.get('employee_id', '').strip()
            employee_phone = request.POST.get('employee_phone', '').strip()
            employee_IDcard = request.POST.get('employee_IDcard', '').strip()
            employee_address = request.POST.get('employee_address', '').strip()

            print(employee_name, role, new_employee_id, employee_phone, employee_IDcard, employee_address)

            # 检查新工号是否已存在
            if (Employee.objects.filter(employee_id=new_employee_id, homestay=employee.homestay).exists()
                    and (new_employee_id != employee.employee_id)):
                messages.error(request, '保存失败，工号已存在！')
                page = request.GET.get('page', '1')
                return redirect(f'{reverse("manager_employee_info", args=[id])}?page={page}')

            # 更新员工信息
            employee.employee_name = employee_name
            employee.role = role
            employee.employee_id = new_employee_id
            employee.employee_phone = employee_phone
            employee.employee_IDcard = employee_IDcard
            employee.employee_address = employee_address
            employee.save()
            messages.success(request, '保存成功！')

        except Exception as e:
            # messages.error(request, f'保存失败，原因：{str(e)}')
            messages.error(request, f'保存失败，请重试')
    # 发送提示信息
    page = request.GET.get('page', '1')
    return redirect(f'{reverse("manager_employee_info", args=[id])}?page={page}')


# 员工列表视图
def query_employee(request):
    employee_list = Employee.objects.filter(homestay_id=request.user.homestay_id)

    # 创建分页器，每页显示5条记录
    paginator = Paginator(employee_list, 5)
    # 从请求中获取页码，默认为第一页
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'active_page': 'employee',  # 当前页面标识
        'active_function': 'query_employee',
        'page_obj': page_obj
    }
    return render(request, 'accounts/manager/manager_query_employee.html', context)


# 账户状态设置视图
def set_is_active(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    # 将员工账户设置为禁用或启用状态
    if employee.is_active:
        employee.is_active = False
        messages.error(request, "该账户已成功禁用！")
    else:
        employee.is_active = True
        messages.success(request, "该账户已成功启用！")
    employee.save()
    # 发送提示信息
    page = request.GET.get('page', '1')
    # 返回拼接url
    return redirect(f'{reverse("manager_query_employee")}?page={page}')


# 删除账户视图
def delete_employee(request, id):
    # 获取对应的员工对象
    employee = Employee.objects.get(id=id)
    try:
        employee.delete()
        messages.error(request, "该账户已删除！")
    except Exception as e:
        messages.error(request, '员工删除失败，请重试！')
    # 发送提示信息
    page = request.GET.get('page', '1')
    # 返回拼接url
    return redirect(f'{reverse("manager_query_employee")}?page={page}')


# 测试视图
def test_view(request):
    messages.info(request, "消息测试!")
    messages.error(request, "错误测试!")
    messages.success(request, "成功测试!")
    return render(request, 'test.html')
