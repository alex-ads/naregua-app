from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import AgendamentoForm
from django.contrib.auth import logout
from .models import Agendamento
from datetime import timedelta, timezone
from .models import Barbeiro
from django.contrib.auth.models import User
from .forms import BarbeiroForm
from datetime import date
from .forms import FiltroAgendamentoForm
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect


@login_required
def area_barbeiros(request):
    if request.method == 'POST':
        form = BarbeiroForm(request.POST)
        if form.is_valid():
            barbeiro = form.save(commit=False)
            barbeiro.user = request.user  # Associando o usuário logado ao barbeiro
            barbeiro.save()
            return redirect('home')  # Redireciona para a página de sucesso
    else:
        form = BarbeiroForm()

    # Obter todos os barbeiros cadastrados
    barbeiros = Barbeiro.objects.filter(user=request.user)
    return render(request, 'area_barbeiros.html', {'form': form, 'barbeiros': barbeiros})
# views.py


@login_required
def excluir_barbeiro(request):
    if request.method == 'POST':
        barbeiro_id = request.POST.get('barbeiro')
        Barbeiro.objects.filter(id=barbeiro_id).delete()
    return redirect('area_barbeiros')


def criar_agendamento(request, username):
    barbearia = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, barbearia=barbearia)
        if form.is_valid():
            agendamento = form.save(commit=False)

            # Verifica se já existe algum agendamento para o barbeiro selecionado
            agendamentos_barbeiro = Agendamento.objects.filter(
                barbeiro=agendamento.barbeiro)

            if agendamentos_barbeiro.exists():
                # Obtém o último agendamento do barbeiro
                ultimo_agendamento = agendamentos_barbeiro.latest(
                    'datetime_agendamento')

                # Verifica se já se passaram 30 minutos desde o último agendamento
                if agendamento.datetime_agendamento < ultimo_agendamento.datetime_agendamento + timedelta(minutes=30):
                    # Se ainda não se passaram 30 minutos, redireciona para a página de erro de agendamento
                    return redirect('erro_agendamento', barbeiro_id=agendamento.barbeiro.id)

            # Verifica se existe algum agendamento após o agendamento proposto
            proximos_agendamentos = agendamentos_barbeiro.filter(
                datetime_agendamento__gte=agendamento.datetime_agendamento)

            if proximos_agendamentos.exists():
                # Obtém o próximo agendamento
                proximo_agendamento = proximos_agendamentos.earliest(
                    'datetime_agendamento')

                # Verifica se há um intervalo de 30 minutos entre os agendamentos
                if proximo_agendamento.datetime_agendamento < agendamento.datetime_agendamento + timedelta(minutes=30):
                    # Se não houver, redireciona para a página de erro de agendamento
                    return redirect('erro_agendamento', barbeiro_id=agendamento.barbeiro.id)

            # Se todas as verificações passarem, salva o agendamento
            agendamento.save()
            mensagem_confirmacao = "Seu agendamento foi feito com sucesso!"
            return render(request, 'agendamento.html', {'form': form, 'mensagem_confirmacao': mensagem_confirmacao})
    else:
        form = AgendamentoForm(barbearia=barbearia)

    return render(request, 'agendamento.html', {'form': form})

def erro_agendamento(request, barbeiro_id):
    # Obtém todos os agendamentos para o barbeiro selecionado naquela barbearia
    agendamentos_barbeiro = Agendamento.objects.filter(barbeiro_id=barbeiro_id)
    return render(request, 'erro_agendamento.html', {'agendamentos_barbeiro': agendamentos_barbeiro})


def mysite(request):
    return render(request, 'index.html')


@login_required
def custom_logout(request):
    logout(request)
    # Redireciona para a página desejada após o logout
    return redirect('mysite')


def get_agendamentos_usuario(user):
    """
    Retorna todos os agendamentos relacionados aos barbeiros associados ao usuário logado.
    Exclui os agendamentos com status True.
    Retorna uma queryset vazia se o usuário não tiver barbeiros associados.
    """
    try:
        # Recupera os barbeiros associados ao usuário logado
        barbeiros = Barbeiro.objects.filter(user=user)
        agendamentos = Agendamento.objects.filter(
            barbeiro__in=barbeiros, status=False)  # Exclui agendamentos com status True
        return agendamentos
    except Barbeiro.DoesNotExist:
        # Retorna uma queryset vazia se o usuário não tiver barbeiros associados
        return Agendamento.objects.none()


def filtrar_agendamentos(agendamentos, tipo_filtro, barbeiro_id=None):
    """
    Filtra os agendamentos com base no tipo de filtro especificado e, opcionalmente, por barbeiro.
    Retorna os agendamentos filtrados.
    """
    now = date.today()  # Obter a data atual

    if tipo_filtro == 'dia':
        # Filtrar agendamentos para o dia atual
        agendamentos = agendamentos.filter(datetime_agendamento__date=now)
    elif tipo_filtro == 'semana':
        # Filtrar agendamentos para a semana atual
        end_of_week = now + timedelta(days=6)  # Próximos 7 dias
        agendamentos = agendamentos.filter(
            datetime_agendamento__range=[now, end_of_week])
    elif tipo_filtro == 'mes':
        # Filtrar agendamentos para o mês atual
        agendamentos = agendamentos.filter(
            datetime_agendamento__month=now.month)
    elif tipo_filtro == 'ano':
        # Filtrar agendamentos para o ano atual
        agendamentos = agendamentos.filter(datetime_agendamento__year=now.year)

    # Filtrar por barbeiro, se o ID do barbeiro for fornecido
    if barbeiro_id is not None:
        agendamentos = agendamentos.filter(barbeiro__id=barbeiro_id)

    return agendamentos


@login_required
def home(request):
    # Todos os barbeiros associados ao usuário logado
    barbeiros_do_usuario = request.user.barbeiros.all()
    # Apenas agendamentos relacionados aos barbeiros do usuário logado e com status False
    agendamentos = Agendamento.objects.filter(
        barbeiro__in=barbeiros_do_usuario, status=False)

    tipo_filtro = request.POST.get('tipo_filtro')
    barbeiro_id = request.POST.get('barbeiro_id')

    if tipo_filtro:
        agendamentos = filtrar_agendamentos(agendamentos, tipo_filtro)

    if barbeiro_id:
        agendamentos = agendamentos.filter(barbeiro_id=barbeiro_id)

    form = FiltroAgendamentoForm()
    return render(request, 'home.html', {'agendamentos': agendamentos, 'form': form, 'barbeiros': barbeiros_do_usuario})


@login_required
def atualizar_status(request, agendamento_id):
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, pk=agendamento_id)
        valor_cobrado = request.POST.get('valor_cobrado')

        # Verifica se o valor do serviço foi fornecido
        if valor_cobrado is None or valor_cobrado == '':
            # Se não foi fornecido, retorne uma resposta de erro
            return HttpResponseBadRequest("O valor do serviço é obrigatório.")

        # Atualiza o status do agendamento e salva o valor do serviço
        agendamento.status = True
        agendamento.valor_cobrado = valor_cobrado
        agendamento.save()

        # Redireciona de volta para a página principal ou para onde você desejar
        return redirect('home')
    else:
        # Se o método da requisição não for POST, retorne uma resposta de erro
        return HttpResponseNotAllowed(['POST'])
