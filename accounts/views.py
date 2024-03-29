from django.shortcuts import render, redirect
from .admin import CustomUserCreationForm
from django.contrib import messages


# Create your views here.

def register(request):
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Define o usuário como desativado
            user.save()
            messages.success(
                request, "Registrado. Entre em contato para ativar conta!")
            form = CustomUserCreationForm()
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(request, "registration/register.html", {"form": form})
