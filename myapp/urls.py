from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.mysite, name='mysite'),
    path('home/', views.home, name='home'),
    path('area-barbeiros/', views.area_barbeiros, name='area_barbeiros'),
    path('registro-servico/', views.adicionar_corte, name='adicionar_corte'),
    path('excluir-barbeiro/', views.excluir_barbeiro, name='excluir_barbeiro'),
    path('erro-agendamento/<int:barbeiro_id>/', views.erro_agendamento, name='erro_agendamento'),
    path('atualizar-status/<int:agendamento_id>/', views.atualizar_status, name='atualizar_status'),
    path('exit/', views.custom_logout, name='exit'),
    path('<str:username>/', views.criar_agendamento, name='criar_agendamento'),
]