from rest_framework import serializers

from .models import Category 

class CreateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    image = serializers.URLField(required=False, allow_blank=True)

class ResponseCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    image = serializers.URLField()

class CreateProductSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=40)
    image=serializers.URLField(blank=False)
    description = serializers.TextField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(default=0)
    category=serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
