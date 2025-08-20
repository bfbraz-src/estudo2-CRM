from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('', views.dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Clientes
    path('clientes/', views.cliente_list_view, name='cliente_list'),
    path('clientes/novo/', views.cliente_create_view, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update_view, name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.cliente_delete_view, name='cliente_delete'),
    
    # Atendimentos
    path('atendimentos/', views.atendimento_list_view, name='atendimento_list'),
    path('atendimentos/novo/', views.atendimento_create_view, name='atendimento_create'),
    path('atendimentos/<int:pk>/editar/', views.atendimento_update_view, name='atendimento_update'),
    path('atendimentos/<int:pk>/excluir/', views.atendimento_delete_view, name='atendimento_delete'),
    
    # API
    path('api/buscar-cep/', views.buscar_cep, name='buscar_cep'),
]