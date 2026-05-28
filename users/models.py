from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email=models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    ggoogle_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    #though we use abstractuser username can not be null, thats why we update it and make it null
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    USERNAME_FIELD='email'
    #only used for creating superuser 
    REQUIRED_FIELDS=[]
