from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.mysite, name='mysite'),
    path('home/', views.home, name='home'),
    path('profissionais/', views.area_profissionais, name='area_profissionais'),
    path('registro-servico/', views.registrar_servico, name='registrar_servico'),
    path('gerenciar-profissional/', views.gerenciar_profissional, name='gerenciar_profissional'),
    path('erro-agendamento/<int:barbeiro_id>/', views.erro_agendamento, name='erro_agendamento'),
    path('atualizar-status/<int:agendamento_id>/', views.atualizar_status, name='atualizar_status'),
    path('exit/', views.custom_logout, name='exit'),
    path('<str:username>/', views.criar_agendamento, name='criar_agendamento'),
]