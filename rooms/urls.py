from django.shortcuts import render
from django.urls import path

from rooms.views import *

urlpatterns = [

    path('add_room_type', add_room_type, name='add_room_type'),
    path('query_room_type', query_room_type, name='query_room_type'),
]
