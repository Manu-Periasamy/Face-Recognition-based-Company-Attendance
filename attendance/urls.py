"""attendance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from re import template
from django.contrib import admin
from django.urls import path
from numpy import rec
from recognition_system import views as recognition_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', recognition_views.home, name='home',),
    path('home/', recognition_views.home, name='home',),
    path('login/',auth_views.LoginView.as_view(template_name='login.html'),name='login'),
    path('not_authorised', recognition_views.not_authorised, name='not-authorised'),
    # path('login/', recognition_views.login_view, name="login"), 
    # path('/', recognition_views.custom_logout, name="logout"),   
    path('logout/', auth_views.LogoutView.as_view(template_name='index.html'), name='logout'),
    path('register/', recognition_views.register, name="register"),
    path('dashboard/', recognition_views.dashboard, name="dashboard"),
    # path('', auth_views.LogoutView.as_view(), name='logout'),
    # path('recognize/', recognition_views.mark_your_attendance, name="recognize"),
    path('create_dataset/<id>/', recognition_views.create_dataset, name="create_dataset"),
    path('view_attendance_date/', recognition_views.view_attendance_date, name='view_attendance_date'),
    path('view_attendance_employee/', recognition_views.view_attendance_employee, name='view_attendance_employee'),
    path('emp_view_attendance_employee/', recognition_views.employee_view_attendance, name='employee_view_employee_attendance'),
    path('in_time/', recognition_views.mark_your_attendance_in, name="mark_attendance_in"),
    path('out_time', recognition_views.mark_your_attendance_out, name="mark_attendance_out"),
    # path('check_blink/', recognition_views.check_blink, name="check_blink"),
]


