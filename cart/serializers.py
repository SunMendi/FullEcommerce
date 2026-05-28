from rest_framework import serializers 
from django.conf import settings 
from .models import Cart 
from django.contrib.auth import get_user_model 
from catalog.models import Product 

User= get_user_model() 

#required=True by default have in the field column 

from catalog.serializers import ResponseProductSerializer

class CreateCartSerializer(serializers.Serializer):
    user=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class ResponseCartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = ResponseProductSerializer(read_only=True)
    size = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


class ResponseCartSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    user_id=serializers.IntegerField(read_only=True)
    items = ResponseCartItemSerializer(source='cartItems', many=True, read_only=True)
    total_price = serializers.DecimalField(source='total_price', max_digits=10, decimal_places=2, read_only=True)

class CreateCartItemSerializer(serializers.Serializer):
    cart=serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())
    product=serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    size = serializers.CharField(required=False, allow_blank=True, max_length=30)
    color = serializers.CharField(required=False, allow_blank=True, max_length=50)
    quantity=serializers.IntegerField(min_value=1)


class AddCartItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    size = serializers.CharField(required=False, allow_blank=True, max_length=30)
    color = serializers.CharField(required=False, allow_blank=True, max_length=50)
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

    
