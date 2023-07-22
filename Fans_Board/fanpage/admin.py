from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'email_verified']

admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(Category)
admin.site.register(CustomUser, CustomUserAdmin)
