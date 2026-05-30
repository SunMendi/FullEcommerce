from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    use_in_migrations = False

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

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
    objects = UserManager()
