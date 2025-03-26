from django.shortcuts import render
from django.urls import path

from rooms.views import *

urlpatterns = [

    # 总览
    # path('room_overview', room_overview, name='room_overview'),


    # 房型
    path('add_room_type', add_room_type, name='add_room_type'),
    path('query_room_type', query_room_type, name='query_room_type'),
    path('room_type_info/<str:type_id>', room_type_info, name='room_type_info'),
    path('edit_room_type_info/<str:type_id>', edit_room_type_info, name='edit_room_type_info'),
    path('delete_room_type/<str:type_id>', delete_room_type, name='delete_room_type'),

    # 房间
    path('query_room/<str:type_id>', query_room, name='query_room'),
    path('add_room/<str:type_id>', add_room, name='add_room'),
    path('update_room/<str:room_id>', update_room, name='update_room'),
    # path('edit_room_info/<str:room_id>', edit_room_info, name='edit_room_info'),
    # path('delete_room/<str:room_id>', delete_room, name='delete_room'),

    # 房态
    path('room_type_overview', room_type_overview, name='room_type_overview'),
]
