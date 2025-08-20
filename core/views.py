from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Cliente, Atendimento
from .forms import CustomUserCreationForm, ClienteForm, AtendimentoForm
import requests

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Erro ao criar conta. Verifique os dados informados.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard_view(request):
    clientes_count = Cliente.objects.count()
    atendimentos_count = Atendimento.objects.count()
    atendimentos_hoje = Atendimento.objects.filter(
        data_hora__date=timezone.now().date()
    ).count()
    
    # Próximos atendimentos
    proximos_atendimentos = Atendimento.objects.filter(
        data_hora__gte=timezone.now(),
        status='agendado'
    ).order_by('data_hora')[:5]
    
    context = {
        'clientes_count': clientes_count,
        'atendimentos_count': atendimentos_count,
        'atendimentos_hoje': atendimentos_hoje,
        'proximos_atendimentos': proximos_atendimentos,
    }
    return render(request, 'core/dashboard.html', context)

# ========== VIEWS DE CLIENTE ==========
@login_required
def cliente_list_view(request):
    search = request.GET.get('search', '')
    clientes = Cliente.objects.all()
    
    if search:
        clientes = clientes.filter(
            Q(nome__icontains=search) |
            Q(email__icontains=search) |
            Q(cpf__icontains=search) |
            Q(telefone__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(clientes, 10)  # 10 clientes por página
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)
    
    return render(request, 'core/cliente_list.html', {
        'clientes': clientes,
        'search': search
    })

@login_required
def cliente_create_view(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente cadastrado com sucesso!')
                return redirect('cliente_list')
            except Exception as e:
                messages.error(request, 'Erro ao salvar cliente. Verifique os dados.')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = ClienteForm()
    return render(request, 'core/cliente_form.html', {'form': form, 'title': 'Cadastrar Cliente'})

@login_required
def cliente_update_view(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('cliente_list')
            except Exception as e:
                messages.error(request, 'Erro ao atualizar cliente.')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'core/cliente_form.html', {'form': form, 'title': 'Editar Cliente'})

@login_required
def cliente_delete_view(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            cliente.delete()
            messages.success(request, 'Cliente excluído com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao excluir cliente. Verifique se não há atendimentos associados.')
        return redirect('cliente_list')
    return render(request, 'core/cliente_confirm_delete.html', {'cliente': cliente})

# ========== VIEWS DE ATENDIMENTO ==========
@login_required
def atendimento_list_view(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    atendimentos = Atendimento.objects.select_related('cliente', 'usuario')
    
    if search:
        atendimentos = atendimentos.filter(
            Q(cliente__nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    if status_filter:
        atendimentos = atendimentos.filter(status=status_filter)
    
    # Ordenar por data (mais próximos primeiro)
    atendimentos = atendimentos.order_by('data_hora')
    
    # Paginação
    paginator = Paginator(atendimentos, 15)  # 15 atendimentos por página
    page_number = request.GET.get('page')
    atendimentos = paginator.get_page(page_number)
    
    return render(request, 'core/atendimento_list.html', {
        'atendimentos': atendimentos,
        'search': search,
        'status_filter': status_filter,
        'status_choices': Atendimento.STATUS_CHOICES,
    })

@login_required
def atendimento_create_view(request):
    if request.method == 'POST':
        form = AtendimentoForm(request.POST)
        if form.is_valid():
            try:
                # Verificar se não há conflito de horário
                data_hora = form.cleaned_data['data_hora']
                conflito = Atendimento.objects.filter(
                    data_hora__date=data_hora.date(),
                    data_hora__time=data_hora.time(),
                    status='agendado'
                ).exists()
                
                if conflito:
                    messages.error(request, 'Já existe um atendimento agendado para este horário.')
                    return render(request, 'core/atendimento_form.html', {'form': form, 'title': 'Agendar Atendimento'})
                
                atendimento = form.save(commit=False)
                atendimento.usuario = request.user
                atendimento.save()
                messages.success(request, 'Atendimento agendado com sucesso!')
                return redirect('atendimento_list')
            except Exception as e:
                messages.error(request, 'Erro ao agendar atendimento.')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = AtendimentoForm()
    return render(request, 'core/atendimento_form.html', {'form': form, 'title': 'Agendar Atendimento'})

@login_required
def atendimento_update_view(request, pk):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if request.method == 'POST':
        form = AtendimentoForm(request.POST, instance=atendimento)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Atendimento atualizado com sucesso!')
                return redirect('atendimento_list')
            except Exception as e:
                messages.error(request, 'Erro ao atualizar atendimento.')
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados informados.')
    else:
        form = AtendimentoForm(instance=atendimento)
    return render(request, 'core/atendimento_form.html', {'form': form, 'title': 'Editar Atendimento'})

@login_required
def atendimento_delete_view(request, pk):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if request.method == 'POST':
        try:
            atendimento.delete()
            messages.success(request, 'Atendimento excluído com sucesso!')
        except Exception as e:
            messages.error(request, 'Erro ao excluir atendimento.')
        return redirect('atendimento_list')
    return render(request, 'core/atendimento_confirm_delete.html', {'atendimento': atendimento})

# API para buscar CEP
def buscar_cep(request):
    cep = request.GET.get('cep', '').replace('-', '').replace('.', '')
    if len(cep) == 8:
        try:
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if not data.get('erro'):
                    return JsonResponse({
                        'success': True,
                        'logradouro': data.get('logradouro', ''),
                        'bairro': data.get('bairro', ''),
                        'cidade': data.get('localidade', ''),
                        'estado': data.get('uf', ''),
                    })
        except requests.RequestException:
            pass
    return JsonResponse({'success': False})
