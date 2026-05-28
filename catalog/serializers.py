from rest_framework import serializers

from .models import Category 

class CreateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    slug = serializers.SlugField(max_length=80, required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)
    active = serializers.BooleanField(required=False)

class ResponseCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    slug = serializers.SlugField(read_only=True)
    image = serializers.URLField()
    active = serializers.BooleanField(read_only=True)

class CreateProductSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=40)
    slug=serializers.SlugField(max_length=80, required=False, allow_blank=True)
    image=serializers.ImageField(required=True)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(default=0)
    sizes = serializers.ListField(child=serializers.CharField(max_length=30), required=False)
    colors = serializers.ListField(child=serializers.CharField(max_length=50), required=False)
    featured = serializers.BooleanField(required=False)
    active = serializers.BooleanField(required=False)
    category=serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())


class ResponseProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=40)
    slug = serializers.SlugField(read_only=True)
    image = serializers.URLField()
    images = serializers.SerializerMethodField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()
    sizes = serializers.ListField(child=serializers.CharField(), read_only=True)
    colors = serializers.ListField(child=serializers.CharField(), read_only=True)
    featured = serializers.BooleanField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    category = ResponseCategorySerializer()

    def get_images(self, obj):
        return [obj.image] if obj.image else []

class CreateProductReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=100)
    body = serializers.CharField()


class AdminReviewUpdateSerializer(serializers.Serializer):
    approved = serializers.BooleanField()


class ResponseProductReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    user_name = serializers.SerializerMethodField()
    rating = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    body = serializers.CharField(read_only=True)
    approved = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_user_name(self, obj):
        return obj.user.username or obj.user.email
