from django.urls import path, include
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/<str:order_id>/', views.payment, name='payment'),
    path('response/', views.response, name='response'),
    path('order_complete/', views.order_complete, name='order_complete'),
]
