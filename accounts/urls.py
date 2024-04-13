from django.urls import path
from accounts import views


urlpatterns = [
    path('', views.register, name='register'),
    # Rota personalizada para login
    path('accounts/login/', views.custom_login, name='login'),

]
