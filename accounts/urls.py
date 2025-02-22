from django.shortcuts import render
from django.urls import path
from django.contrib.auth import views as auth_views

# from accounts.views import login_view, add_employee, register_view, manager, test_view, edit_employee
from accounts.views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),


    # 保洁
    path('cleaner/', lambda request: render(request, 'accounts/cleaner/cleaner.html'), name='cleaner'),

    # 民宿管理员
    path('manager/', manager, name='manager'),
    path('manager/manager_add_employee', add_employee, name='manager_add_employee'),
    path('manager/manager_employee_info/<str:id>', employee_info, name='manager_employee_info'),
    path('manager/manager_edit_employee/<str:id>', edit_employee, name='manager_edit_employee'),
    path('manager/manager_query_employee', query_employee, name='manager_query_employee'),
    path('manager/manager_query_employee/set_is_active/<str:id>', set_is_active, name='set_is_active'),
    path('manager/manager_query_employee/delete_employee/<str:id>', delete_employee, name='delete_employee'),

    # 前台
    path('reception/', lambda request: render(request, 'accounts/reception/reception.html'), name='reception'),

    # path('test/', lambda request: render(request, 'test.html'), name='test'),
    path('test/', test_view, name='test'),
    path('base/', lambda request: render(request, 'base.html'), name='base'),
]
