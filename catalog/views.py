from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import CreateCategorySerializer, ResponseCategorySerializer, CreateProductSerializer, ResponseProductSerializer, CreateProductReviewSerializer, ResponseProductReviewSerializer, AdminReviewUpdateSerializer
from .services import create_category, get_all_category, create_product, get_category, get_public_products, get_public_product_by_slug, get_public_categories, get_public_category_by_slug, get_product_reviews_by_slug, create_product_review, delete_product_review, update_category, delete_category, update_product, delete_product, get_product_reviews_by_id, update_review_approval
import logging


logger = logging.getLogger(__name__)


class ListCreateCategoryView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []

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
            logger.exception("Unexpected error while creating category")
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

class DetailCategoryView(APIView):
    def get(self, request):
        id = request.query_params.get("id")
        try:
            category = get_category(id)
            return Response(
                {
                    "message": "Category fetched successfully",
                    "data": {
                        "id": category.id,
                        "name": category.name
                    }
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Unexpected error while fetching category detail")
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryManageView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, slug):
        try:
            category, products = get_public_category_by_slug(slug)
            category_result = ResponseCategorySerializer(category)
            product_result = ResponseProductSerializer(products, many=True)
            return Response(
                {
                    "category": category_result.data,
                    "products": product_result.data
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryDetailManageView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        serializer = CreateCategorySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            category = update_category(id, serializer.validated_data)
            result = ResponseCategorySerializer(category)
            return Response(
                {
                    "message": "Category updated successfully",
                    "data": result.data
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            delete_category(id)
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class ListCreateProductView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []

    def post(self, request):
        serializer=CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product=create_product(serializer.validated_data)
            result = ResponseProductSerializer(product)
            return Response(
                {
                    "message": "Product created successfully",
                    "data": result.data,
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            # 4. Handle expected Business/Database errors (Status 400)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # 5. Handle unexpected System errors (Status 500)
            logger.exception("Unexpected error while creating product")
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailManageView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        serializer = CreateProductSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            product = update_product(id, serializer.validated_data)
            result = ResponseProductSerializer(product)
            return Response(
                {
                    "message": "Product updated successfully",
                    "data": result.data
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Unexpected error while updating product")
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            delete_product(id)
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicProductListView(APIView):
    def get(self, request):
        try:
            category = request.query_params.get('category')
            search = request.query_params.get('search')
            featured_param = request.query_params.get('featured')
            sort = request.query_params.get('sort')

            if sort and sort not in ['newest', 'price_asc', 'price_desc']:
                raise ValueError("Invalid sort value. Use newest, price_asc, or price_desc.")

            try:
                limit = int(request.query_params.get('limit', 20))
                offset = int(request.query_params.get('offset', 0))
            except ValueError:
                raise ValueError("Limit and offset must be valid numbers.")

            if limit < 1:
                raise ValueError("Limit must be greater than 0.")

            if offset < 0:
                raise ValueError("Offset cannot be negative.")

            featured = None
            if featured_param is not None:
                if featured_param.lower() not in ['true', 'false']:
                    raise ValueError("Featured must be true or false.")
                featured = featured_param.lower() == 'true'

            products, total = get_public_products(
                category_slug=category,
                search=search,
                featured=featured,
                limit=limit,
                offset=offset,
                sort=sort
            )

            result = ResponseProductSerializer(products, many=True)
            return Response(
                {
                    "items": result.data,
                    "total": total
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicProductDetailView(APIView):
    def get(self, request, slug):
        try:
            product = get_public_product_by_slug(slug)
            result = ResponseProductSerializer(product)
            return Response(result.data, status=status.HTTP_200_OK)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicCategoryListView(APIView):
    def get(self, request):
        try:
            categories = get_public_categories()
            result = ResponseCategorySerializer(categories, many=True)
            return Response(result.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicCategoryDetailView(APIView):
    def get(self, request, slug):
        try:
            category, products = get_public_category_by_slug(slug)
            category_result = ResponseCategorySerializer(category)
            product_result = ResponseProductSerializer(products, many=True)
            return Response(
                {
                    "category": category_result.data,
                    "products": product_result.data
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewListView(APIView):
    def get(self, request, slug):
        try:
            reviews, average, count = get_product_reviews_by_slug(slug)
            result = ResponseProductReviewSerializer(reviews, many=True)
            return Response(
                {
                    "reviews": result.data,
                    "average": round(float(average), 2),
                    "count": count
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewListByIdView(APIView):
    def get(self, request, id):
        try:
            reviews, average, count = get_product_reviews_by_id(id)
            result = ResponseProductReviewSerializer(reviews, many=True)
            return Response(
                {
                    "reviews": result.data,
                    "average": round(float(average), 2),
                    "count": count
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permission() for permission in self.permission_classes]

    def get(self, request, id):
        try:
            reviews, average, count = get_product_reviews_by_id(id)
            result = ResponseProductReviewSerializer(reviews, many=True)
            return Response(
                {
                    "reviews": result.data,
                    "average": round(float(average), 2),
                    "count": count
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, id):
        serializer = CreateProductReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = create_product_review(
                product_id=id,
                user_id=request.user.id,
                validated_data=serializer.validated_data
            )
            result = ResponseProductReviewSerializer(review)
            return Response(
                {
                    "message": "Review submitted successfully and waiting for approval",
                    "data": result.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            delete_product_review(review_id=id, user_id=request.user.id)
            return Response(
                {"message": "Review deleted successfully"},
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminProductReviewView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        serializer = AdminReviewUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = update_review_approval(id, serializer.validated_data['approved'])
            result = ResponseProductReviewSerializer(review)
            return Response(
                {
                    "message": "Review updated successfully",
                    "data": result.data
                },
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
