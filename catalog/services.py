from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import Category

def create_category(category_data: dict) -> Category:
    """
    Creates a new category in the database.
    """
    try:
        # **category_data unpacking: 
        # Converts {'name': 'Tech'} into Category.objects.create(name='Tech')
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
