from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.get_book, name='book'),
    path('book/<int:id>', views.detail_book, name='detail_book'),
    path('api/book_data', views.insert_book_data, name='insert_book_data')
]
