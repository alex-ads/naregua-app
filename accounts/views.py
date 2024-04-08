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