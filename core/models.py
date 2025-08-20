from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Cliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome completo")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 'Formato: (11) 99999-9999')],
        verbose_name="Telefone"
    )
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 'Formato: 000.000.000-00')],
        verbose_name="CPF"
    )
    
    # Endereço
    cep = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{5}-\d{3}$', 'Formato: 00000-000')],
        verbose_name="CEP"
    )
    logradouro = models.CharField(max_length=200, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Atendimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_hora = models.DateTimeField(verbose_name="Data e Hora do Atendimento")
    descricao = models.TextField(verbose_name="Descrição do Atendimento")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Atendido por")
    
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado', verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Atendimento"
        verbose_name_plural = "Atendimentos"
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.cliente.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
