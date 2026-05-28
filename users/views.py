from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = ProfileSerializer(request.user)
        return Response(result.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = request.user
        for field, value in serializer.validated_data.items():
            setattr(user, field, value)

        user.save()
        result = ProfileSerializer(user)
        return Response(
            {
                "message": "Profile updated successfully",
                "data": result.data
            },
            status=status.HTTP_200_OK
        )
