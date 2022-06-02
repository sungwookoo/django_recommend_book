from django.contrib import admin

# Register your models here.
from user.models import UserModel

admin.site.register(UserModel)
