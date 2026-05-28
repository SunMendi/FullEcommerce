from rest_framework import serializers
from catalog.serializers import ResponseProductSerializer
from .models import Order, OrderItem, Payment

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True, allow_blank=False)
    payment_method = serializers.ChoiceField(choices=['cod', 'bank_transfer'], required=True)


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    size = serializers.CharField(required=False, allow_blank=True, max_length=30)
    color = serializers.CharField(required=False, allow_blank=True, max_length=50)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    customer_phone = serializers.CharField(required=True, allow_blank=False, max_length=20)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=True, allow_blank=False)
    shipping_city = serializers.CharField(required=True, allow_blank=False, max_length=80)
    note = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=['cod', 'bkash', 'nagad'])
    transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=100)
    sender_phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    items = CreateOrderItemSerializer(many=True)


class ResponseOrderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = ResponseProductSerializer(read_only=True)
    product_name = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    size = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


class PaymentProofSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=True, allow_blank=False)
    payment_receipt = serializers.FileField(required=True)


class ResponsePaymentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    sender_phone = serializers.CharField(read_only=True)
    payment_receipt = serializers.FileField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class ResponseOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    customer_phone = serializers.CharField(read_only=True)
    customer_email = serializers.EmailField(read_only=True)
    status = serializers.CharField(read_only=True)
    shipping_address = serializers.CharField(read_only=True)
    shipping_city = serializers.CharField(read_only=True)
    note = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    delivery_charge = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    items = ResponseOrderItemSerializer(many=True, read_only=True)
    payments = ResponsePaymentSerializer(many=True, read_only=True)


class CreateOrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order_number = serializers.CharField(read_only=True)
    total = serializers.DecimalField(source='total_price', max_digits=10, decimal_places=2, read_only=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'confirmed', 'paid', 'shipped', 'delivered', 'cancelled'])
