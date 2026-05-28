from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.response import Response 
from .serializers import CreateCartSerializer, ResponseCartSerializer, ResponseCartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .services import create_cart, get_single_cart, delete_cart, add_item_to_cart, update_cart_item_quantity, remove_cart_item

# Create your views here.

class ListCreateCartView(APIView):
    def post(self, request):
        serializer=CreateCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            #here we just convert complex python object into json compatible data, jeta diye easily json e convert kora jabe,ekta class er object e method,runtime,meta soho onek kicu thake,json encoder ta buje na, so age json compatible like list, dict and primitive type e convert kore nite hoi , then json e convert korte hoi...
            cart=create_cart(serializer.validated_data)
            result=ResponseCartSerializer(cart)
            return Response (
                {
                    "message":"successfully created",
                    "data":result.data
                }, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            # 4. Handle expected Business/Database errors (Status 400)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 5. Handle unexpected System errors (Status 500)
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class DetailCartView(APIView):
    def get(self, request, id):
        try:
            cart = get_single_cart(id)
            result = ResponseCartSerializer(cart) 
            return Response({"data": result.data}, status=status.HTTP_200_OK)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self, request, id):
        try:
            delete_cart(id)
            return Response(
                {"message": "Cart deleted successfully"}, 
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddCartItemView(APIView):
    def post(self, request, cart_id):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product_id = serializer.validated_data['product'].id
            quantity = serializer.validated_data['quantity']
            size = serializer.validated_data.get('size', '')
            color = serializer.validated_data.get('color', '')
            
            cart_item = add_item_to_cart(
                cart_id=cart_id, 
                product_id=product_id, 
                quantity=quantity,
                size=size,
                color=color
            )
            
            result = ResponseCartItemSerializer(cart_item)
            return Response(
                {
                    "message": "Item added successfully to cart",
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


class DetailCartItemView(APIView):
    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quantity = serializer.validated_data['quantity']
            cart_item = update_cart_item_quantity(cart_item_id=item_id, quantity=quantity)
            
            result = ResponseCartItemSerializer(cart_item)
            return Response(
                {
                    "message": "Cart item quantity updated successfully",
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

    def delete(self, request, item_id):
        try:
            remove_cart_item(cart_item_id=item_id)
            return Response(
                {"message": "Cart item removed successfully"}, 
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
