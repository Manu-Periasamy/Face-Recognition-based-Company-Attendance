from users.models import Profile
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django import forms  
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from django.contrib import messages
from django.db import models

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email',  'department']

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Profile
        fields = UserChangeForm.Meta.fields