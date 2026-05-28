from django.db import models
from django.conf import settings


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True) 

    @property
    def total_price(self):
        # Sum the subtotals of all cart items
        return sum(item.subtotal for item in self.cartItems.all()) 


#'catalog.Product'- this is called string lateral represntation , mainly used for importing class and function

class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartItems')
    product=models.ForeignKey('catalog.Product',on_delete=models.CASCADE, related_name='cartItems')
    size=models.CharField(max_length=30, blank=True)
    color=models.CharField(max_length=50, blank=True)
    quantity=models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        # Calculate subtotal (quantity * price of the product)
        return self.quantity * self.product.price

    class Meta:
        constraints= [
            models.UniqueConstraint(fields=['cart','product','size','color'],
            name='unique_cart_product_size_color')
        ]
