from asyncio import AbstractServer
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models


class MyProfile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE, related_name='profile')
    description = models.CharField(max_length=100)


@receiver(post_save, sender=User)
def my_handler(sender, **kwargs):
    """
    Quando Criar um usuário no Django, vai rodar essa função
    para criar uma instancia nesse modelo MyProfile no campo "user".
    """
    if kwargs.get('created', False):
        MyProfile.objects.create(user=kwargs['instance'])


class Barbeiro(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='barbeiros')
    nome_barbeiro = models.CharField(max_length=30)
    activated = models.BooleanField(default=True)  # Campo booleano para indicar se o barbeiro está ativado ou não

    def __str__(self):
        return self.nome_barbeiro


class Agendamento(models.Model):
    barbeiro = models.ForeignKey(
        Barbeiro, on_delete=models.CASCADE, related_name='agendamentos')
    datetime_agendamento = models.DateTimeField()
    nome_cliente = models.CharField(max_length=30)
    telefone = models.CharField(max_length=20)
    valor_cobrado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    # False para não concluído, True para concluído
    status = models.BooleanField(default=False)
    # False para não houve cancelamento, True para houve cancelamento
    cancelamento = models.BooleanField(default=False)

    def __str__(self):
        return f"Agendamento para {self.barbeiro.nome_barbeiro} em {self.datetime_agendamento}"
