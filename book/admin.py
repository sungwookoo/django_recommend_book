from django.contrib import admin
from .models import BookData, Review, Like

# Register your models here.

admin.site.register(Like)
admin.site.register(Review)
admin.site.register(BookData)
