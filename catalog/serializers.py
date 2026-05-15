from rest_framework import serializers

class CreateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    image = serializers.URLField(required=False, allow_blank=True)

class ResponseCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    image = serializers.URLField()
