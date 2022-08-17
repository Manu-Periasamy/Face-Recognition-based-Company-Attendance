from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Profile

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Profile
    list_display = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
admin.site.register(Profile, CustomUserAdmin)