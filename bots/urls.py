from django.urls import path
from .views import FacebookWebhookView

urlpatterns = [
    path('webhooks/facebook/', FacebookWebhookView.as_view(), name='facebook-webhook'),
]
