from django.contrib import admin
from .models import Cliente, Atendimento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'cidade', 'estado', 'created_at']
    list_filter = ['estado', 'cidade', 'created_at']
    search_fields = ['nome', 'email', 'cpf']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'data_hora', 'status', 'usuario', 'created_at']
    list_filter = ['status', 'data_hora', 'usuario']
    search_fields = ['cliente__nome', 'descricao']
    readonly_fields = ['created_at', 'updated_at']