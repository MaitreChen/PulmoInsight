# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Patient


class CustomUserAdmin(UserAdmin):
    # Define the fields displayed in the user list
    list_display = ('username', 'email', 'is_doctor', 'is_staff')


# register the CustomUser model and associate it with the custom CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Patient)
