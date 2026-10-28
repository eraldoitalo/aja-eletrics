from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), path('entrar/', views.SignIn.as_view(), name='login'),
    path('sair/', views.sign_out, name='logout'), path('tema/', views.theme, name='theme'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('veiculos/', views.vehicles, name='vehicles'), path('veiculos/novo/', views.vehicle_create, name='vehicle_create'),
    path('veiculos/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('veiculos/<int:pk>/aquisicao/', views.acquisition_detail, name='acquisition_detail'),
    path('veiculos/<int:pk>/vender/', views.sale_create, name='sale_create'),
    path('clientes/', views.customers, name='customers'), path('clientes/novo/', views.customer_create, name='customer_create'),
    path('clientes/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('oficina/', views.orders, name='orders'), path('oficina/nova/', views.order_create, name='order_create'),
    path('oficina/<int:pk>/', views.order_detail, name='order_detail'),
    path('oficina/<int:pk>/orcamento/', views.budget_create, name='budget_create'),
    path('oficina/<int:pk>/acao/<str:action>/', views.order_action, name='order_action'),
]
