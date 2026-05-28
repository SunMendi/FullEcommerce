from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import CheckoutSerializer, ResponseOrderSerializer, PaymentProofSerializer, ResponsePaymentSerializer, CreateOrderSerializer, CreateOrderResponseSerializer, OrderStatusUpdateSerializer
from .services import checkout_cart, get_order_details, get_user_orders, submit_payment_proof, create_public_order, get_all_orders, update_order_status, track_guest_order
from .throttles import CheckoutRateThrottle, OrderTrackRateThrottle

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Validate payload
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            shipping_address = serializer.validated_data['shipping_address']
            payment_method = serializer.validated_data['payment_method']
            
            # 2. Call Service to perform checkout
            order = checkout_cart(
                user_id=request.user.id, 
                shipping_address=shipping_address,
                payment_method=payment_method
            )
            
            # 3. Serialize and return response
            result = ResponseOrderSerializer(order)
            return Response(
                {
                    "message": "Order created successfully from checkout",
                    "data": result.data
                }, 
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == 'POST':
            return [CheckoutRateThrottle()]
        return []

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return [permission() for permission in self.permission_classes]

    def get(self, request):
        try:
            # 1. Fetch user orders
            orders = get_user_orders(user_id=request.user.id)
            
            # 2. Serialize list of orders
            result = ResponseOrderSerializer(orders, many=True)
            return Response(
                {
                    "message": "Orders fetched successfully",
                    "data": result.data
                }, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = create_public_order(serializer.validated_data)
            result = CreateOrderResponseSerializer(order)
            return Response(result.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            # 1. Fetch order details (only allows current logged in user's order)
            order = get_order_details(order_id=id, user_id=request.user.id)
            
            # 2. Serialize order
            result = ResponseOrderSerializer(order)
            return Response(
                {
                    "message": "Order details fetched successfully",
                    "data": result.data
                }, 
                status=status.HTTP_200_OK
            )
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitPaymentProofView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Required for processing file uploads!

    def post(self, request, id):
        # 1. Validate input containing file & text
        serializer = PaymentProofSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            transaction_id = serializer.validated_data['transaction_id']
            payment_receipt = serializer.validated_data['payment_receipt']
            
            # 2. Call service to process upload
            payment = submit_payment_proof(
                order_id=id,
                user_id=request.user.id,
                transaction_id=transaction_id,
                payment_receipt=payment_receipt
            )
            
            # 3. Return serialized payment details
            result = ResponsePaymentSerializer(payment)
            return Response(
                {
                    "message": "Payment proof submitted successfully.",
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


class GuestOrderTrackView(APIView):
    throttle_classes = [OrderTrackRateThrottle]

    def get(self, request):
        order_number = request.query_params.get('order_number')
        phone = request.query_params.get('phone')

        try:
            order = track_guest_order(order_number=order_number, phone=phone)
            result = ResponseOrderSerializer(order)
            return Response(
                {
                    "order": result.data,
                    "items": result.data.get('items', [])
                },
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except LookupError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            status_filter = request.query_params.get('status')
            orders = get_all_orders(status_filter=status_filter)
            result = ResponseOrderSerializer(orders, many=True)
            return Response(
                {
                    "message": "Orders fetched successfully",
                    "data": result.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": "An internal server error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = update_order_status(order_id=id, new_status=serializer.validated_data['status'])
            result = ResponseOrderSerializer(order)
            return Response(
                {
                    "message": "Order status updated successfully",
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
