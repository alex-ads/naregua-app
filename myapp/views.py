from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AgendamentoForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Agendamento
from django.http import JsonResponse
from django.utils import timezone
from .forms import FiltroAgendamentoForm
from datetime import timedelta




# Create your views here.
def mysite(request):
    return render(request, 'index.html')


def agendamento(request, username):
    cliente = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.usuario = cliente
            agendamento.save()
            # Redirecione para a página de sucesso ou outra URL desejada
            return redirect('/')
    else:
        form = AgendamentoForm()
    return render(request, 'agendamento.html', {'cliente': cliente, 'form': form})


@login_required
def custom_logout(request):
    logout(request)
    # Redireciona para a página desejada após o logout
    return redirect('mysite')


@login_required
def home(request):
    agendamentos = Agendamento.objects.filter(usuario=request.user)
    tipo_filtro = request.POST.get('tipo_filtro', None)

    if request.method == 'POST' and tipo_filtro:
        now = timezone.now()
        if tipo_filtro == 'dia':
            agendamentos = agendamentos.filter(data_agendamento__date=now.date())
        elif tipo_filtro == 'semana':
            end_of_week = now + timedelta(days=6)  # Próximos 7 dias
            agendamentos = agendamentos.filter(data_agendamento__range=[now, end_of_week])
        elif tipo_filtro == 'mes':
            agendamentos = agendamentos.filter(data_agendamento__month=now.month)
        elif tipo_filtro == 'ano':
            agendamentos = agendamentos.filter(data_agendamento__year=now.year)

    return render(request, 'home.html', {'agendamentos': agendamentos, 'tipo_filtro': tipo_filtro})
