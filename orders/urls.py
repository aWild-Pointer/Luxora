from django.urls import path

from orders.views import *

urlpatterns = [
    path('create_order', create_order , name='create_order'),
    path('query_order', query_order , name='query_order'),
    path('order_info/<str:order_id>', order_info , name='order_info'),


    path('load_room_type', load_room_type, name='load_room_type'),
    path('cancel_order/<str:order_id>', cancel_order, name='cancel_order')

]