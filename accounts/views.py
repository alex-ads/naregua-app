from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .admin import CustomUserCreationForm
from django.contrib import messages
from django.db.utils import IntegrityError


# Create your views here.

def register(request):
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Define o usuário como desativado
                user.save()
                messages.success(
                    request, "Registrado com Sucesso! Entre em contato para ativar conta.")
                form = CustomUserCreationForm()
            except IntegrityError as e:
                # Tratar erros de integridade, como tentativa de registro com email duplicado
                messages.error(request, f"Erro ao registrar: {e}")
            except Exception as e:
                # Lidar com outras exceções não esperadas
                messages.error(request, f"Erro inesperado ao registrar: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, "registration/register.html", {"form": form})


def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirecione para a página desejada após o login bem-sucedido
                # Substitua 'dashboard' pelo nome da sua view de dashboard
                return redirect('home')
            else:
                # Usuário não autenticado
                messages.error(
                    request, "Credenciais inválidas.")
        else:
            # Formulário inválido, há erros
            # Você pode acessar os erros do formulário assim:
            # Obtém os erros gerais do formulário
            errors = form.errors.get('__all__')
            # ou acessar os erros de campos individuais:
            # username_errors = form.errors.get('username')
            # password_errors = form.errors.get('password')
            # etc.
            messages.error(
                request, "Credenciais inválidas.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
