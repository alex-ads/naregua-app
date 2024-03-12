from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.mysite, name='mysite'),
    path('home/', views.home, name='home'),
    path('exit/', views.custom_logout, name='exit'),
    path('<str:username>/', views.agendamento, name='agendamento'),
]