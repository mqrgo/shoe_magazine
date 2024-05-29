from django.urls import path
from users import views


app_name = 'users'

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('lk/', views.lk, name='lk'),
]
