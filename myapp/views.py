from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AgendamentoForm
from django.contrib.auth import logout
from .models import Agendamento
from datetime import timedelta
from .models import Barbeiro
from django.contrib.auth.models import User
from .forms import BarbeiroForm
from datetime import date
from .forms import FiltroAgendamentoForm
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.translation import gettext as _
from django.urls import reverse




def criar_agendamento(request, username):
    barbearia = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, barbearia=barbearia)
        if form.is_valid():
            agendamento = form.save(commit=False)

            # Verifica se já existe algum agendamento para o barbeiro selecionado no mesmo dia
            agendamentos_barbeiro = Agendamento.objects.filter(
                barbeiro=agendamento.barbeiro,
                datetime_agendamento__date=agendamento.datetime_agendamento.date()
            )

            if agendamentos_barbeiro.exists():
                # Verifica se o horário do novo agendamento entra em conflito com os agendamentos existentes
                for agendamento_existente in agendamentos_barbeiro:
                    if agendamento_existente.datetime_agendamento - timedelta(minutes=30) < agendamento.datetime_agendamento < agendamento_existente.datetime_agendamento + timedelta(minutes=30):
                        # Se houver conflito, redireciona para a página de erro de agendamento
                        data_selecionada = agendamento.datetime_agendamento.date()
                        url = reverse('erro_agendamento', args=[agendamento.barbeiro.id])
                        url += f'?data_selecionada={data_selecionada}'
                        return redirect(url)

            # Se todas as verificações passarem, salva o agendamento
            agendamento.save()
            mensagem_confirmacao = "Seu agendamento foi feito com sucesso!"
            return render(request, 'agendamento.html', {'form': form, 'mensagem_confirmacao': mensagem_confirmacao})
    else:
        form = AgendamentoForm(barbearia=barbearia)

    return render(request, 'agendamento.html', {'form': form})



def erro_agendamento(request, barbeiro_id):
    data_selecionada = request.GET.get('data_selecionada')
    agendamentos_barbeiro = Agendamento.objects.filter(barbeiro_id=barbeiro_id, datetime_agendamento__date=data_selecionada).exclude(cancelamento=True)
    
    return render(request, 'erro_agendamento.html', {'agendamentos_barbeiro': agendamentos_barbeiro, 'data_selecionada': data_selecionada})


def adicionar_corte(request):
    if request.method == 'POST':
        datetime_agendamento = request.POST.get('datetime_agendamento')
        nome_cliente = request.POST.get('nome_cliente')
        telefone = request.POST.get('telefone')
        barbeiro_id = request.POST.get('barbeiro')

        # Verifica se todos os campos obrigatórios estão preenchidos
        if datetime_agendamento and nome_cliente and telefone and barbeiro_id:
            # Cria um novo objeto de Agendamento com os dados recebidos do formulário
            agendamento = Agendamento.objects.create(
                datetime_agendamento=datetime_agendamento,
                nome_cliente=nome_cliente,
                telefone=telefone,
                barbeiro_id=barbeiro_id
            )
            # Redireciona para alguma página de sucesso ou para outro lugar após salvar os dados
            # Altere 'pagina_sucesso' para a rota desejada
            return redirect('home')
        else:
            # Se algum campo estiver em branco, exiba uma mensagem de erro ou trate adequadamente
            return render(request, 'home.html', {'mensagem': 'Todos os campos são obrigatórios!'})

    else:
        # Obter os barbeiros associados ao usuário autenticado
        barbeiros = Barbeiro.objects.filter(user=request.user)
        return render(request, 'user_adm/adicionar_corte.html', {'barbeiros': barbeiros})


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
    return render(request, 'user_adm/area_barbeiros.html', {'form': form, 'barbeiros': barbeiros})
# views.py


@login_required
def excluir_barbeiro(request):
    if request.method == 'POST':
        barbeiro_id = request.POST.get('barbeiro')
        Barbeiro.objects.filter(id=barbeiro_id).delete()
    return redirect('area_barbeiros')


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
        barbeiro__in=barbeiros_do_usuario, status=False, cancelamento=False)

    tipo_filtro = request.POST.get('tipo_filtro')
    barbeiro_id = request.POST.get('barbeiro_id')

    if tipo_filtro:
        agendamentos = filtrar_agendamentos(agendamentos, tipo_filtro)

    if barbeiro_id:
        agendamentos = agendamentos.filter(barbeiro_id=barbeiro_id)

    # Organize os agendamentos por dia da semana e data
    agendamentos_por_dia = {}
    for agendamento in agendamentos:
        dia_semana = agendamento.datetime_agendamento.strftime('%A')
        dia_semana = _(dia_semana)  # Traduzindo o nome do dia da semana para português
        data = agendamento.datetime_agendamento.strftime('%d/%m/%Y')
        if dia_semana not in agendamentos_por_dia:
            agendamentos_por_dia[dia_semana] = {}
        if data not in agendamentos_por_dia[dia_semana]:
            agendamentos_por_dia[dia_semana][data] = []
        agendamentos_por_dia[dia_semana][data].append(agendamento)

    form = FiltroAgendamentoForm()
    return render(request, 'home.html', {'agendamentos_por_dia': agendamentos_por_dia, 'form': form, 'barbeiros': barbeiros_do_usuario})


@login_required
def atualizar_status(request, agendamento_id):
    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, pk=agendamento_id)
        acao = request.POST.get('acao')

        if acao == 'concluir':
            valor_cobrado = request.POST.get('valor_cobrado')
            if not valor_cobrado:
                return HttpResponseBadRequest("O valor do serviço é obrigatório para concluir o agendamento.")
            else:
                # Atualiza o status do agendamento e salva o valor do serviço
                agendamento.status = True
                agendamento.valor_cobrado = valor_cobrado
                agendamento.save()
        elif acao == 'cancelar':
            # Marcar o agendamento como cancelado
            agendamento.cancelamento = True
            agendamento.save()

        # Redireciona de volta para a página principal ou para onde você desejar
        return redirect('home')
    else:
        # Se o método da requisição não for POST, retorne uma resposta de erro
        return HttpResponseNotAllowed(['POST'])

