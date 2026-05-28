from decimal import Decimal
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from cart.models import Cart
from catalog.models import Product
from .models import Order, OrderItem, Payment

DELIVERY_FREE_THRESHOLD = Decimal('2000.00')
DELIVERY_CHARGE = Decimal('120.00')


def calculate_delivery_charge(subtotal: Decimal) -> Decimal:
    if subtotal >= DELIVERY_FREE_THRESHOLD:
        return Decimal('0.00')
    return DELIVERY_CHARGE


def generate_order_number() -> str:
    today = timezone.localdate()
    prefix = f"ARA-{today.strftime('%y%m%d')}"
    last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()

    if last_order and last_order.order_number:
        try:
            next_number = int(last_order.order_number.split('-')[-1]) + 1
        except ValueError:
            next_number = 1
    else:
        next_number = 1

    while True:
        order_number = f"{prefix}-{next_number:04d}"
        if not Order.objects.filter(order_number=order_number).exists():
            return order_number
        next_number += 1


def create_public_order(validated_data: dict) -> Order:
    items = validated_data.get('items', [])
    if not items:
        raise ValueError("At least one item is required to place an order.")

    payment_method = validated_data.get('payment_method')
    if payment_method not in ['cod', 'bkash', 'nagad']:
        raise ValueError("Invalid payment method selected.")

    transaction_id = validated_data.get('transaction_id', '')
    sender_phone = validated_data.get('sender_phone', '')
    if payment_method in ['bkash', 'nagad'] and not transaction_id:
        raise ValueError("Transaction ID is required for bKash or Nagad payment.")

    with transaction.atomic():
        subtotal = Decimal('0.00')
        prepared_items = []

        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')

            try:
                product = Product.objects.select_for_update().get(
                    id=product_id,
                    active=True,
                    category__active=True
                )
            except ObjectDoesNotExist:
                raise LookupError(f"Product with ID {product_id} does not exist.")

            if product.stock < quantity:
                raise ValueError(f"Only {product.stock} item(s) available for {product.name}.")

            size = item.get('size', '') or ''
            color = item.get('color', '') or ''
            if product.sizes and size not in product.sizes:
                raise ValueError(f"Invalid size selected for {product.name}.")
            if product.colors and color not in product.colors:
                raise ValueError(f"Invalid color selected for {product.name}.")

            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            prepared_items.append({
                'product': product,
                'product_name': product.name,
                'price': product.price,
                'size': size,
                'color': color,
                'quantity': quantity,
            })

        delivery_charge = calculate_delivery_charge(subtotal)
        total = subtotal + delivery_charge
        order = Order.objects.create(
            order_number=generate_order_number(),
            customer_name=validated_data['customer_name'],
            customer_phone=validated_data['customer_phone'],
            customer_email=validated_data.get('customer_email', ''),
            shipping_address=validated_data['shipping_address'],
            shipping_city=validated_data['shipping_city'],
            note=validated_data.get('note', ''),
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            total_price=total
        )

        for prepared_item in prepared_items:
            product = prepared_item['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=prepared_item['product_name'],
                price=prepared_item['price'],
                size=prepared_item['size'],
                color=prepared_item['color'],
                quantity=prepared_item['quantity']
            )
            product.stock -= prepared_item['quantity']
            product.save(update_fields=['stock'])

        Payment.objects.create(
            order=order,
            amount=order.total_price,
            payment_method=payment_method,
            status='pending',
            transaction_id=transaction_id or None,
            sender_phone=sender_phone
        )

        return order

def checkout_cart(user_id: int, shipping_address: str, payment_method: str) -> Order:
    """
    Transaction-safe checkout. Converts a user's active Cart into an Order,
    snapshots current product pricing, creates a Payment record, and clears the cart.
    """
    if not shipping_address or shipping_address.strip() == "":
        raise ValueError("Shipping address is required for checkout.")
    
    if payment_method not in ['cod', 'bank_transfer']:
        raise ValueError("Invalid payment method selected.")

    # We wrap the checkout in an atomic transaction.
    with transaction.atomic():
        # 1. Fetch Cart
        try:
            cart = Cart.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            raise ValueError("You do not have an active cart.")

        # 2. Check if Cart is empty
        cart_items = cart.cartItems.all()
        if not cart_items.exists():
            raise ValueError("Your cart is empty. Cannot checkout.")

        delivery_charge = calculate_delivery_charge(cart.total_price)
        total_price = cart.total_price + delivery_charge

        # 3. Create the Order
        order = Order.objects.create(
            order_number=generate_order_number(),
            user_id=user_id,
            shipping_address=shipping_address,
            subtotal=cart.total_price,
            delivery_charge=delivery_charge,
            total_price=total_price
        )

        # 4. Copy CartItems to OrderItems and snapshot product prices
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                price=cart_item.product.price, # Price snapshot
                size=getattr(cart_item, 'size', ''),
                color=getattr(cart_item, 'color', ''),
                quantity=cart_item.quantity
            )

        # 5. Create the initial Payment record
        Payment.objects.create(
            order=order,
            amount=order.total_price,
            payment_method=payment_method,
            status='pending'
        )

        # 6. Clear the Cart (Deleting the cart automatically deletes all CartItems due to CASCADE)
        cart.delete()

        return order


def get_order_details(order_id: int, user_id: int) -> Order:
    """
    Fetches a specific order for a user.
    """
    try:
        order = Order.objects.get(id=order_id, user_id=user_id)
        return order
    except ObjectDoesNotExist:
        raise LookupError(f"Order #{order_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_user_orders(user_id: int):
    """
    Fetches all orders belonging to a user.
    """
    try:
        return Order.objects.filter(user_id=user_id)
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_all_orders(status_filter=None):
    try:
        orders = Order.objects.all().prefetch_related('items', 'payments')
        if status_filter:
            orders = orders.filter(status=status_filter)
        return orders
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def update_order_status(order_id: int, new_status: str) -> Order:
    allowed_statuses = ['pending', 'confirmed', 'paid', 'shipped', 'delivered', 'cancelled']
    if new_status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            old_status = order.status

            if old_status != 'cancelled' and new_status == 'cancelled':
                for item in order.items.select_related('product').all():
                    product = item.product
                    product.stock += item.quantity
                    product.save(update_fields=['stock'])

            if old_status == 'cancelled' and new_status != 'cancelled':
                for item in order.items.select_related('product').all():
                    product = item.product
                    if product.stock < item.quantity:
                        raise ValueError(f"Only {product.stock} item(s) available for {product.name}.")
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])

            order.status = new_status
            order.save(update_fields=['status', 'updated_at'])
            return order
    except ObjectDoesNotExist:
        raise LookupError(f"Order #{order_id} does not exist.")
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def track_guest_order(order_number: str, phone: str) -> Order:
    if not order_number or not phone:
        raise ValueError("Order number and phone are required.")

    try:
        return Order.objects.prefetch_related('items', 'payments').get(
            order_number=order_number,
            customer_phone=phone
        )
    except ObjectDoesNotExist:
        raise LookupError("Order not found with the provided order number and phone.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def submit_payment_proof(order_id: int, user_id: int, transaction_id: str, payment_receipt) -> Payment:
    """
    Submits manual payment proof (transaction ID & receipt) for an Order.
    """
    try:
        # 1. Fetch the Order (ensuring it belongs to the logged-in user)
        order = Order.objects.get(id=order_id, user_id=user_id)
    except ObjectDoesNotExist:
        raise LookupError(f"Order #{order_id} does not exist.")

    # 2. Get or create the Payment record for this order
    payment, created = Payment.objects.get_or_create(
        order=order,
        payment_method='bank_transfer',
        defaults={'amount': order.total_price}
    )

    # 3. Update verification fields and reset status to pending
    payment.transaction_id = transaction_id
    payment.payment_receipt = payment_receipt
    payment.status = 'pending'

    try:
        payment.save()
        return payment
    except IntegrityError:
        raise ValueError("This transaction ID has already been used on another payment.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while saving payment: {str(e)}")
