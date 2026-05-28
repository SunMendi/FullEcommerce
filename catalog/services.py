from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg
from .models import Category,Product,ProductReview
import cloudinary.uploader

def create_category(category_data: dict) -> Category:
    """
    Creates a new category in the database.
    """
    try:
        # If 'image' is an uploaded file, upload it to Cloudinary first
        image_file = category_data.get('image')
        if image_file and not isinstance(image_file, str):
            upload_result = cloudinary.uploader.upload(image_file)
            category_data['image'] = upload_result.get('secure_url')

        category = Category.objects.create(**category_data)
        return category
        
    except IntegrityError as e:
        # Catch database constraints (e.g., unique violations)
        # We raise a ValueError so the View can catch it and return a 400 status.
        raise ValueError(f"Database error while creating category: {str(e)}")
        
    except Exception as e:
        # Catch any other unexpected system errors
        raise Exception(f"An unexpected error occurred: {str(e)}")
    
def get_all_category():
    try:
        category=Category.objects.all()
        return category

    except Exception as e:
        raise Exception(f"{str(e)}")
    
def create_product(validated_data: dict)->Product:
    try:
        # If 'image' is an uploaded file, upload it to Cloudinary first
        image_file = validated_data.get('image')
        if image_file and not isinstance(image_file, str):
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result.get('secure_url')

        product=Product.objects.create(**validated_data)
        return product 
    except IntegrityError as e:
        raise ValueError(f"Database integrity error: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
    

def get_category(id:int)->Category:
    try:
        category=Category.objects.get(id=id)
        return category 
    except ObjectDoesNotExist as e:
        raise LookupError(f"value does not exist: {str(e)}")
    except Exception as e:
        raise Exception(f"an unexpected error occured: {str(e)}")


def update_category(category_id: int, validated_data: dict) -> Category:
    try:
        category = Category.objects.get(id=category_id)

        image_file = validated_data.get('image')
        if image_file and not isinstance(image_file, str):
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result.get('secure_url')

        for field, value in validated_data.items():
            setattr(category, field, value)

        category.save()
        return category
    except ObjectDoesNotExist:
        raise LookupError(f"Category with ID {category_id} does not exist.")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating category: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def delete_category(category_id: int) -> bool:
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return True
    except ObjectDoesNotExist:
        raise LookupError(f"Category with ID {category_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while deleting category: {str(e)}")


def get_public_products(category_slug=None, search=None, featured=None, limit=20, offset=0, sort=None):
    try:
        products = Product.objects.filter(active=True, category__active=True).select_related('category')

        if category_slug:
            products = products.filter(category__slug=category_slug)

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        if featured is not None:
            products = products.filter(featured=featured)

        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        else:
            products = products.order_by('-created_at')

        total = products.count()
        products = products[offset:offset + limit]

        return products, total
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_public_product_by_slug(slug: str) -> Product:
    try:
        return Product.objects.select_related('category').get(slug=slug, active=True, category__active=True)
    except ObjectDoesNotExist:
        raise LookupError(f"Product with slug {slug} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def update_product(product_id: int, validated_data: dict) -> Product:
    try:
        product = Product.objects.get(id=product_id)

        image_file = validated_data.get('image')
        if image_file and not isinstance(image_file, str):
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result.get('secure_url')

        for field, value in validated_data.items():
            setattr(product, field, value)

        product.save()
        return product
    except ObjectDoesNotExist:
        raise LookupError(f"Product with ID {product_id} does not exist.")
    except IntegrityError as e:
        raise ValueError(f"Database error while updating product: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def delete_product(product_id: int) -> bool:
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return True
    except ObjectDoesNotExist:
        raise LookupError(f"Product with ID {product_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while deleting product: {str(e)}")


def get_public_categories():
    try:
        return Category.objects.filter(active=True).order_by('name')
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_public_category_by_slug(slug: str):
    try:
        category = Category.objects.get(slug=slug, active=True)
        products = Product.objects.filter(category=category, active=True).select_related('category').order_by('-created_at')
        return category, products
    except ObjectDoesNotExist:
        raise LookupError(f"Category with slug {slug} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_product_reviews_by_slug(slug: str):
    try:
        product = Product.objects.get(slug=slug, active=True, category__active=True)
        reviews = ProductReview.objects.filter(product=product, approved=True).select_related('user', 'product')
        review_stats = reviews.aggregate(average=Avg('rating'))
        average = review_stats['average'] or 0
        count = reviews.count()
        return reviews, average, count
    except ObjectDoesNotExist:
        raise LookupError(f"Product with slug {slug} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def get_product_reviews_by_id(product_id: int):
    try:
        product = Product.objects.get(id=product_id, active=True, category__active=True)
        reviews = ProductReview.objects.filter(product=product, approved=True).select_related('user', 'product')
        review_stats = reviews.aggregate(average=Avg('rating'))
        average = review_stats['average'] or 0
        count = reviews.count()
        return reviews, average, count
    except ObjectDoesNotExist:
        raise LookupError(f"Product with ID {product_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def create_product_review(product_id: int, user_id: int, validated_data: dict) -> ProductReview:
    try:
        product = Product.objects.get(id=product_id, active=True, category__active=True)
        review = ProductReview.objects.create(
            product=product,
            user_id=user_id,
            rating=validated_data['rating'],
            title=validated_data['title'],
            body=validated_data['body'],
            approved=False
        )
        return review
    except ObjectDoesNotExist:
        raise LookupError(f"Product with ID {product_id} does not exist.")
    except IntegrityError:
        raise ValueError("You have already reviewed this product.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def delete_product_review(review_id: int, user_id: int) -> bool:
    try:
        review = ProductReview.objects.get(id=review_id, user_id=user_id)
        review.delete()
        return True
    except ObjectDoesNotExist:
        raise LookupError(f"Review with ID {review_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def update_review_approval(review_id: int, approved: bool) -> ProductReview:
    try:
        review = ProductReview.objects.select_related('user', 'product').get(id=review_id)
        review.approved = approved
        review.save(update_fields=['approved', 'updated_at'])
        return review
    except ObjectDoesNotExist:
        raise LookupError(f"Review with ID {review_id} does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
