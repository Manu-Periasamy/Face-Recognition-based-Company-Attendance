from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import PermissionsMixin

from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class Profile(AbstractUser):
    # location = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=30)

class Present(models.Model):
	user=models.ForeignKey(Profile,on_delete=models.CASCADE)
	date = models.DateField(default=datetime.date.today)
	present=models.BooleanField(default=False)
	
class Time(models.Model):
	user=models.ForeignKey(Profile,on_delete=models.CASCADE)
	date = models.DateField(default=datetime.date.today)
	time=models.DateTimeField(null=True,blank=True)
	out=models.BooleanField(default=False)
	