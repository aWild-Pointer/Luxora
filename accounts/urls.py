from django.urls import path

from accounts.views.cleaner_view import cleaner
from accounts.views.reception_views import *
# from accounts.views import login_view, add_employee, register_view, manager, test_view, edit_employee
from accounts.views.views import *
from accounts.views.manager_views import *

urlpatterns = [
    path('', login_view, name='login'),
    path('register', register_view, name='register'),
    path('logout', logout_view, name='logout'),
    path('update_self_info', update_self_info, name='update_self_info'),
    path('updte_password', update_password, name='update_password'),
    path('reset_password/<str:id>', reset_password, name='reset_password'),

    # 保洁
    path('cleaner', cleaner, name='cleaner'),

    # 民宿管理员
    path('manager', manager, name='manager'),
    path('manager/manager_add_employee', add_employee, name='manager_add_employee'),
    path('manager/manager_employee_info/<str:id>', employee_info, name='manager_employee_info'),
    path('manager/manager_update_employee_info/<str:id>', update_employee_info, name='manager_edit_employee'),
    path('manager/manager_query_employee', manager_query_employee, name='manager_query_employee'),
    path('manager/manager_query_employee/set_is_active/<str:id>', set_is_active, name='set_is_active'),
    path('manager/manager_query_employee/delete_employee/<str:id>', delete_employee, name='delete_employee'),

    # 前台
    path('reception', reception, name='reception'),
    path('reception/check_in', query_check_in, name='query_check_in'),
    path('reception/check_in/<str:order_id>', CheckInView.as_view(), name='check_in'),
    path('reception/book', book, name='book'),

    path('reception/check_out', query_check_out, name='query_check_out'),
    path('reception/check_out/<str:order_id>', check_out, name='check_out'),




    # path('test/', lambda request: render(request, 'test.html'), name='test'),
    path('test', test_view, name='test'),
    path('base', lambda request: render(request, 'base.html'), name='base'),
]
