from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    dob = models.DateField(blank=True,null=True)
    phone_number = models.DecimalField(max_digits=10,decimal_places=0,blank=True,null=True)
