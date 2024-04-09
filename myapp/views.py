from django.utils import timezone
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
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotAllowed
from django.utils.translation import gettext as _
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError


def criar_agendamento(request, username):
    try:
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
                            url = reverse('erro_agendamento', args=[
                                          agendamento.barbeiro.id])
                            url += f'?data_selecionada={data_selecionada}'
                            return redirect(url)

                # Se todas as verificações passarem, salva o agendamento
                agendamento.save()
                mensagem_confirmacao = "Seu agendamento foi feito com sucesso!"
                return render(request, 'cliente/agendamento.html', {'form': form, 'mensagem_confirmacao': mensagem_confirmacao})
        else:
            form = AgendamentoForm(barbearia=barbearia)

        return render(request, 'cliente/agendamento.html', {'form': form})

    except ValidationError as ve:
        # Tratar validações de formulário
        form = AgendamentoForm(barbearia=barbearia)  # Instanciar o formulário novamente
        mensagem_erro = "Ocorreu um erro de validação: {}".format(ve)
        return render(request, 'cliente/agendamento.html', {'form': form, 'mensagem_erro': mensagem_erro})

    except Http404:
        raise  # Se não encontrou o usuário, deixe a exceção ser propagada

    except Exception as e:
        # Em caso de qualquer outra exceção, retornar uma resposta de erro adequada
        form = AgendamentoForm(barbearia=barbearia)  # Instanciar o formulário novamente
        mensagem_erro = "Ocorreu um erro ao processar o agendamento: {}".format(
            e)
        return render(request, 'cliente/agendamento.html', {'form': form, 'mensagem_erro': mensagem_erro})

def erro_agendamento(request, barbeiro_id):
    try:
        data_selecionada = request.GET.get('data_selecionada')
        agendamentos_barbeiro = Agendamento.objects.filter(
            barbeiro_id=barbeiro_id, datetime_agendamento__date=data_selecionada).exclude(cancelamento=True)

        return render(request, 'cliente/erro_agendamento.html', {'agendamentos_barbeiro': agendamentos_barbeiro, 'data_selecionada': data_selecionada})

    except Exception as e:
        # Em caso de qualquer exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao processar a página de erro de agendamento: {}".format(
            e)
        return render(request, 'cliente/erro_agendamento.html', {'mensagem_erro': mensagem_erro})


@login_required
def adicionar_corte(request):
    try:
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
                # Adiciona uma mensagem de sucesso
                messages.success(request, 'Serviço adicionado com sucesso!')
                # Obter os barbeiros associados ao usuário autenticado
                barbeiros = Barbeiro.objects.filter(user=request.user)
                # Renderiza o template novamente com a mensagem de sucesso e os barbeiros
                return render(request, 'user_adm/adicionar_corte.html', {'barbeiros': barbeiros})
            else:
                # Se algum campo estiver em branco, exiba uma mensagem de erro ou trate adequadamente
                return render(request, 'user_adm/adicionar_corte.html', {'mensagem': 'Todos os campos são obrigatórios!'})
        else:
            # Obter os barbeiros associados ao usuário autenticado
            barbeiros = Barbeiro.objects.filter(user=request.user)
            return render(request, 'user_adm/adicionar_corte.html', {'barbeiros': barbeiros})

    except Exception as e:
        # Em caso de qualquer exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao processar a adição de corte: {}".format(
            e)
        return render(request, 'user_adm/adicionar_corte.html', {'mensagem_erro': mensagem_erro})


@login_required
def area_barbeiros(request):
    try:
        if request.method == 'POST':
            form = BarbeiroForm(request.POST)
            if form.is_valid():
                barbeiro = form.save(commit=False)
                barbeiro.user = request.user
                barbeiro.save()
                # Adiciona uma mensagem de sucesso
                messages.success(request, 'Barbeiro adicionado com sucesso!')
                return redirect('area_barbeiros')
        else:
            form = BarbeiroForm()

        barbeiros = Barbeiro.objects.filter(user=request.user)
        return render(request, 'user_adm/area_barbeiros.html', {'form': form, 'barbeiros': barbeiros})

    except Exception as e:
        # Em caso de qualquer exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao processar a área de barbeiros: {}".format(
            e)
        return render(request, 'user_adm/area_barbeiros.html', {'mensagem_erro': mensagem_erro})


@login_required
def excluir_barbeiro(request):
    try:
        if request.method == 'POST':
            barbeiro_id = request.POST.get('barbeiro')
            Barbeiro.objects.filter(id=barbeiro_id).delete()
        return redirect('area_barbeiros')

    except Exception as e:
        # Em caso de qualquer exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao excluir o barbeiro: {}".format(e)
        return render(request, 'user_adm/area_barbeiros.html', {'mensagem_erro': mensagem_erro})


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
    except User.DoesNotExist:
        # Retorna uma queryset vazia se o usuário não existir
        return Agendamento.objects.none()
    except Exception as e:
        # Em caso de qualquer outra exceção, retornar uma queryset vazia e registrar o erro
        print(f"Erro ao recuperar os agendamentos do usuário: {e}")
        return Agendamento.objects.none()


def filtrar_agendamentos(agendamentos, tipo_filtro, barbeiro_id=None):
    """
    Filtra os agendamentos com base no tipo de filtro especificado e, opcionalmente, por barbeiro.
    Retorna os agendamentos filtrados.
    """
    try:
        now = timezone.now()  # Obter a data e hora atual

        if tipo_filtro == 'dia':
            # Filtrar agendamentos para o dia atual
            agendamentos = agendamentos.filter(
                datetime_agendamento__date=now.date())
        elif tipo_filtro == 'semana':
            # Filtrar agendamentos para a semana atual
            end_of_week = now + timezone.timedelta(days=6)  # Próximos 7 dias
            agendamentos = agendamentos.filter(
                datetime_agendamento__range=[now, end_of_week])
        elif tipo_filtro == 'mes':
            # Filtrar agendamentos para o mês atual
            agendamentos = agendamentos.filter(
                datetime_agendamento__month=now.month)
        elif tipo_filtro == 'ano':
            # Filtrar agendamentos para o ano atual
            agendamentos = agendamentos.filter(
                datetime_agendamento__year=now.year)

        # Filtrar por barbeiro, se o ID do barbeiro for fornecido
        if barbeiro_id is not None:
            agendamentos = agendamentos.filter(barbeiro__id=barbeiro_id)

        return agendamentos

    except Exception as e:
        # Em caso de qualquer outra exceção, retornar uma queryset vazia e registrar o erro
        print(f"Erro ao filtrar agendamentos: {e}")
        return Agendamento.objects.none()


@login_required
def home(request):
    try:
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
            # Traduzindo o nome do dia da semana para português
            dia_semana = _(dia_semana)
            data = agendamento.datetime_agendamento.strftime('%d/%m/%Y')
            if dia_semana not in agendamentos_por_dia:
                agendamentos_por_dia[dia_semana] = {}
            if data not in agendamentos_por_dia[dia_semana]:
                agendamentos_por_dia[dia_semana][data] = []
            agendamentos_por_dia[dia_semana][data].append(agendamento)

        form = FiltroAgendamentoForm()
        return render(request, 'user_adm/home.html', {'agendamentos_por_dia': agendamentos_por_dia, 'form': form, 'barbeiros': barbeiros_do_usuario})

    except Exception as e:
        # Em caso de qualquer outra exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao processar a página inicial: {}".format(
            e)
        return render(request, 'erro.html', {'mensagem_erro': mensagem_erro})


@login_required
def atualizar_status(request, agendamento_id):
    try:
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

    except Exception as e:
        # Em caso de qualquer outra exceção, retornar uma resposta de erro adequada
        mensagem_erro = "Ocorreu um erro ao atualizar o status do agendamento: {}".format(
            e)
        return render(request, 'erro.html', {'mensagem_erro': mensagem_erro})
