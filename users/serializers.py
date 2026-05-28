from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source='username', required=False, allow_blank=True, allow_null=True, max_length=150)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(source='phone_number', required=False, allow_blank=True, allow_null=True, max_length=20)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True, max_length=80)
