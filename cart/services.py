from .models import Cart,CartItem 
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from catalog.models import Product

def create_cart(validated_data):
    try:
        cart=Cart.objects.create(**validated_data)
        return cart
    except IntegrityError as e:
        # Raising an exception allows the View's try-except block to catch it
        raise ValueError("A cart already exists for this user.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while creating the cart: {str(e)}")
    


def get_single_cart(id):
    try:
        cart=Cart.objects.get(id=id)
        return cart 
    except ObjectDoesNotExist as e:
        raise LookupError(f"Cart with ID {id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
        

def delete_cart(cart_id: int) -> bool:
    """
    Deletes a specific Cart from the database.
    """
    try:
        # 1. Fetch the Cart
        cart = Cart.objects.get(id=cart_id)
        # 2. Delete it
        cart.delete()
        return True
    except ObjectDoesNotExist:
        # If it doesn't exist, raise a LookupError (404)
        raise LookupError(f"Cart with ID {cart_id} does not exist.")
    except Exception as e:
        # If anything else fails, raise a generic Exception (500)
        raise Exception(f"An unexpected error occurred while deleting the cart: {str(e)}")


def add_item_to_cart(cart_id: int, product_id: int, quantity: int, size: str = '', color: str = '') -> CartItem:
    """
    Adds a product to the cart. If already in cart, increments the quantity.
    """
    try:
        # 1. Fetch Cart
        try:
            cart = Cart.objects.get(id=cart_id)
        except ObjectDoesNotExist:
            raise LookupError(f"Cart with ID {cart_id} does not exist.")

        # 2. Fetch Product
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            raise LookupError(f"Product with ID {product_id} does not exist.")

        size = size or ''
        color = color or ''
        if product.sizes and size not in product.sizes:
            raise ValueError(f"Invalid size selected for {product.name}.")
        if product.colors and color not in product.colors:
            raise ValueError(f"Invalid color selected for {product.name}.")

        # 3. Create or increment CartItem
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    except LookupError as e:
        raise e
    except IntegrityError as e:
        raise ValueError(f"Database error while adding item to cart: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def update_cart_item_quantity(cart_item_id: int, quantity: int) -> CartItem:
    """
    Updates the quantity of a specific CartItem.
    """
    try:
        # 1. Fetch CartItem
        cart_item = CartItem.objects.get(id=cart_item_id)
        
        # 2. Set new quantity
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item

    except ObjectDoesNotExist:
        raise LookupError(f"CartItem with ID {cart_item_id} does not exist.")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating quantity: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def remove_cart_item(cart_item_id: int) -> bool:
    """
    Removes a specific CartItem from the database.
    """
    try:
        # 1. Fetch CartItem
        cart_item = CartItem.objects.get(id=cart_item_id)
        # 2. Delete it
        cart_item.delete()
        return True
    except ObjectDoesNotExist:
        raise LookupError(f"CartItem with ID {cart_item_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while removing cart item: {str(e)}")
    
