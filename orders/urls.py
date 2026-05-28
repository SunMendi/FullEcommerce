from django.urls import path
from .views import CheckoutView, OrderHistoryView, OrderDetailView, SubmitPaymentProofView, GuestOrderTrackView, AdminOrderListView, AdminOrderStatusView

urlpatterns = [
    path('admin/orders', AdminOrderListView.as_view(), name='admin-order-list-no-slash'),
    path('admin/orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:id>/status', AdminOrderStatusView.as_view(), name='admin-order-status-no-slash'),
    path('admin/orders/<int:id>/status/', AdminOrderStatusView.as_view(), name='admin-order-status'),
    path('orders', OrderHistoryView.as_view(), name='order-history-no-slash'),
    path('orders/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/track', GuestOrderTrackView.as_view(), name='order-track-no-slash'),
    path('orders/track/', GuestOrderTrackView.as_view(), name='order-track'),
    path('orders/checkout/', CheckoutView.as_view(), name='order-checkout'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:id>/payment-proof/', SubmitPaymentProofView.as_view(), name='order-payment-proof'),
]
