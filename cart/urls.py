from django.urls import path 
from .views import ListCreateCartView, DetailCartView, AddCartItemView, DetailCartItemView

urlpatterns = [
    path('cart/', ListCreateCartView.as_view(), name='cart-list-create'),
    path('cart/<int:id>/', DetailCartView.as_view(), name='cart-detail'),
    path('cart/<int:cart_id>/items/', AddCartItemView.as_view(), name='cart-item-add'),
    path('cart/items/<int:item_id>/', DetailCartItemView.as_view(), name='cart-item-detail'),
]
