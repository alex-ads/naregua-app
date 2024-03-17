from django import forms
from .models import Agendamento, Barbeiro


class AgendamentoForm(forms.ModelForm):
    nome_cliente = forms.CharField(label="Seu Nome")

    def __init__(self, *args, **kwargs):
        barbearia = kwargs.pop('barbearia', None)
        super(AgendamentoForm, self).__init__(*args, **kwargs)
        if barbearia:
            self.fields['barbeiro'].queryset = Barbeiro.objects.filter(user=barbearia)

    class Meta:
        model = Agendamento
        fields = ['datetime_agendamento', 'nome_cliente', 'telefone', 'barbeiro']
        widgets = {
            'datetime_agendamento': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


class FiltroAgendamentoForm(forms.Form):
    tipo_filtro = forms.ChoiceField(choices=[
        ('dia', 'Dia'),
        ('semana', 'Semana'),
        ('mes', 'Mês'),
        ('ano', 'Ano'),
    ], widget=forms.RadioSelect)


class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = ['nome_barbeiro']