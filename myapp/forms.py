from django import forms
from .models import Agendamento


class AgendamentoForm(forms.ModelForm):
    nome_cliente = forms.CharField(label="Seu Nome")

    class Meta:
        model = Agendamento
        fields = ['data_agendamento', 'nome_cliente', 'telefone']
        widgets = {
            'data_agendamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }



class FiltroAgendamentoForm(forms.Form):
    tipo_filtro = forms.ChoiceField(choices=[
        ('dia', 'Dia'),
        ('semana', 'Semana'),
        ('mes', 'Mês'),
        ('ano', 'Ano'),
    ], widget=forms.RadioSelect)
