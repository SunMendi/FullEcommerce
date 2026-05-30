from django.db import models
from django.conf import settings
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name =models.CharField(blank=False, max_length=40)
    slug=models.SlugField(max_length=80, unique=True, blank=True)
    image=models.URLField(max_length=1000)
    active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"category-{self.pk or 'new'}"
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

class Product(models.Model):
    name=models.CharField(blank=False, max_length=40)
    slug=models.SlugField(max_length=80, unique=True, blank=True)
    image=models.URLField(max_length=1000, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    sizes=models.JSONField(default=list, blank=True)
    colors=models.JSONField(default=list, blank=True)
    featured=models.BooleanField(default=False)
    active=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE, related_name='products')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"product-{self.pk or 'new'}"
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class ProductReview(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE, related_name='reviews')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='product_reviews')
    rating=models.PositiveSmallIntegerField()
    title=models.CharField(max_length=100)
    body=models.TextField()
    approved=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['product','user'], name='unique_product_user_review')
        ]

    def __str__(self):
        return f"{self.rating} star review for {self.product.name}"
