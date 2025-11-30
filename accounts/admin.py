from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Users

#Regisering the Users model in the admin site
admin.site.register(Users)
