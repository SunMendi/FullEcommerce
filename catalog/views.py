from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateCategorySerializer, ResponseCategorySerializer,CreateProductSerializer
from .services import create_category, get_all_category,create_product


class ListCreateView(APIView):
    def post(self, request):
        # 1. Initialize and Validate data using the Serializer
        serializer = CreateCategorySerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        
        try:
            # 2. Call the Service Layer to create the Category
            category = create_category(serializer.validated_data)
            
            # 3. Return a professional Success Response
            return Response(
                {
                    "message": "Category created successfully",
                    "data": {
                        "id": category.id,
                        "name": category.name
                    }
                }, 
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            # 4. Handle expected Business/Database errors (Status 400)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # 5. Handle unexpected System errors (Status 500)
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request):
        try:
            # 1. Fetch all categories from the service layer
            categories = get_all_category()
            
            # 2. Serialize the list of categories (many=True is critical for lists!)
            result = ResponseCategorySerializer(categories, many=True)
            
            # 3. Return a structured Success Response
            return Response(
                {
                    "message": "Categories fetched successfully",
                    "data": result.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # 4. Handle unexpected System errors
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListCreateProductView(APIView):
    def post(self, request):
        serializer=CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product=create_product(serializer.validated_data)
            return Response(
                {
                    "data":product.data,
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            # 4. Handle expected Business/Database errors (Status 400)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # 5. Handle unexpected System errors (Status 500)
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)