from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up_view, name='sign-up'),
    path('sign-in/', views.sign_in_view, name='sign-in'),
    path('logout/', views.logout, name='logout'),
    path('user/follow/<int:id>/', views.user_follow, name='user-follow'),
    path('profile/<int:id>/', views.profile_view, name='profile'),
    # path('profile/', views.profile_view, name='profile'),
]
