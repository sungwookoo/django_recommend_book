from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.get_book, name='book'),
    path('book/<int:id>', views.detail_book, name='detail_book'),
    path('api/book_data', views.insert_book_data, name='insert_book_data'),
    path('api/crawling_data', views.insert_crawling_data, name='insert_crawling_data'),
    path('book/review/<int:id>',views.write_review,name='write_review'),
    path('book/review/delete/<int:id>',views.delete_review,name='delete_review'),
    path('book/review/edit/<int:id>',views.edit_review,name='edit_review'),
    path('book/review/edit/update/<int:id>',views.update,name='update'),
    path('book/likes/<int:book_id>',views.likes,name='likes'),
]
