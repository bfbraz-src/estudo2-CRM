from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Cliente, Atendimento
import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[validate_email])
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=30, required=True, label="Sobrenome")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Customizar mensagens de ajuda
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Apenas letras, dígitos e @/./+/-/_ permitidos.'
        self.fields['password1'].help_text = 'Sua senha deve conter pelo menos 8 caracteres.'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está cadastrado.')
        return email

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome completo',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'email@exemplo.com',
                'required': True
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '(99) 99999-9999', 
                #'pattern': '[0-9]{2}[0-9]{5}[0-9]{4}',
                #'data-mask': '(00) 00000-0000',
                'required': True,
                'maxlength': '15'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '000.000.000-00', 
                #'pattern': '[0-9]{3}[0-9]{3}[0-9]{3}[0-9]{2}',
                #'data-mask': '000.000.000-00',
                'required': True,
                'maxlength': '14'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '00000-000', 
                #'pattern': '[0-9]{5}[0-9]{3}',
                #'data-mask': '00000-000',
                'required': True,
                'maxlength': '9'
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Rua, Avenida, etc.',
                'required': True
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '123',
                'required': True
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Apto, Casa, etc.'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Bairro',
                'required': True
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Cidade',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': True
                }, choices=[
                ('', 'Selecione...'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
        }
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remove todos os caracteres não numéricos
            telefone_numbers = re.sub(r'\D', '', telefone)
            
            # Validação do telefone (10 ou 11 dígitos)
            if len(telefone_numbers) < 10 or len(telefone_numbers) > 11:
                raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
            
            return telefone
        return telefone
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            # Remove caracteres não numéricos
            cep_numbers = re.sub(r'\D', '', cep)
            
            # Validação básica do CEP
            if len(cep_numbers) != 8:
                raise ValidationError('CEP deve ter 8 dígitos.')
            
            return cep
        return cep
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove pontos e hífens
            cpf_numbers = re.sub(r'\D', '', cpf)
            
            # Validação básica de CPF
            if len(cpf_numbers) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            
            # Verifica se todos os números não são iguais
            if cpf_numbers == cpf_numbers[0] * 11:
                raise ValidationError('CPF inválido.')
            
            # Algoritmo de validação do CPF
            #if not self.validar_cpf(cpf_numbers):
            #    raise ValidationError('CPF inválido.')
            
            # Verifica se o CPF já existe (exceto para o próprio registro)
            existing_cpf = Cliente.objects.filter(cpf=cpf)
            if self.instance and self.instance.pk:
                existing_cpf = existing_cpf.exclude(pk=self.instance.pk)
            
            if existing_cpf.exists():
                raise ValidationError('Este CPF já está cadastrado.')
        
        return cpf
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Verifica se o email já existe (exceto para o próprio registro)
            existing_email = Cliente.objects.filter(email=email)
            if self.instance and self.instance.pk:
                existing_email = existing_email.exclude(pk=self.instance.pk)
            
            if existing_email.exists():
                raise ValidationError('Este email já está cadastrado.')
        
        return email
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if not estado:
            raise ValidationError('Estado é obrigatório.')
        return estado
    
    def validar_cpf(self, cpf):
        """
        Algoritmo completo de validação do CPF
        """
        # Calcula o primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        
        primeiro_digito = 11 - (soma % 11)
        if primeiro_digito >= 10:
            primeiro_digito = 0
        
        if int(cpf[9]) != primeiro_digito:
            return False
        
        # Calcula o segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        
        segundo_digito = 11 - (soma % 11)
        if segundo_digito >= 10:
            segundo_digito = 0
        
        if int(cpf[10]) != segundo_digito:
            return False
        
        return True

class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['cliente', 'data_hora', 'descricao', 'status']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'data_hora': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local',
                'required': True
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Descreva detalhadamente o atendimento...',
                'required': True
            }),
            'status': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
        self.fields['cliente'].empty_label = "Selecione um cliente..."
    
    def clean_data_hora(self):
        data_hora = self.cleaned_data.get('data_hora')
        if data_hora:
            from django.utils import timezone
            if data_hora < timezone.now():
                raise ValidationError('A data e hora não podem ser no passado.')
        return data_hora