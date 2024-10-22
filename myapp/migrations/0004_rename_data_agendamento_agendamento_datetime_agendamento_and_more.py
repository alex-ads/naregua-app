# Generated by Django 5.0.3 on 2024-03-14 02:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_rename_numero_contato_agendamento_telefone'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='agendamento',
            old_name='data_agendamento',
            new_name='datetime_agendamento',
        ),
        migrations.RemoveField(
            model_name='agendamento',
            name='usuario',
        ),
        migrations.AddField(
            model_name='agendamento',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='agendamento',
            name='valor_cobrado',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.CreateModel(
            name='Barbeiro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_barbeiro', models.CharField(max_length=30)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='barbeiro', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='agendamento',
            name='barbeiro',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='agendamentos', to='myapp.barbeiro'),
            preserve_default=False,
        ),
    ]
