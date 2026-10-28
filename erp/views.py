from decimal import Decimal
from datetime import timedelta
from hashlib import sha256
from functools import wraps
from zoneinfo import ZoneInfo
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, OuterRef, Q, Subquery, Sum
from django.db.models.functions import TruncMonth, TruncWeek
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from . import forms, services
from .models import Acquisition, Budget, BudgetItem, Customer, LoginThrottle, Sale, User, Vehicle, WorkOrder


def roles(*allowed):
    def decorator(view):
        @login_required
        @never_cache
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            services.allow(request.user, *allowed)
            if request.method == 'POST' and not request.user.is_administrative:
                if any(any(part in key.lower() for part in ['purchase', 'compra', 'cost', 'margin', 'lucro']) for key in request.POST):
                    raise PermissionDenied('Campo administrativo não autorizado.')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


class SignIn(LoginView):
    template_name = 'registration/login.html'
    authentication_form = forms.LoginForm
    redirect_authenticated_user = True

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('username', '').strip().lower()
        key = sha256(f'{request.META.get("REMOTE_ADDR", "")}:{identifier}'.encode()).hexdigest()
        record, _ = LoginThrottle.objects.get_or_create(key=key)
        record = LoginThrottle.objects.select_for_update().get(pk=record.pk)
        if timezone.now() - record.started_at >= timedelta(minutes=15):
            record.failures, record.started_at = 0, timezone.now()
        if record.failures >= 10:
            return HttpResponse('Muitas tentativas. Aguarde 15 minutos para tentar novamente.', status=429)
        form = self.get_form()
        if form.is_valid():
            record.failures, record.started_at = 0, timezone.now()
            record.save()
            return self.form_valid(form)
        record.failures += 1
        record.save()
        return self.form_invalid(form)


@require_POST
@login_required
def sign_out(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    if request.user.is_administrative:
        return redirect('dashboard')
    return redirect('orders' if request.user.role == User.Role.MECHANIC else 'vehicles')


@require_POST
@login_required
def theme(request):
    target = request.POST.get('next', '/')
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        target = '/'
    response = HttpResponseRedirect(target)
    response.set_cookie('aja_theme', 'dark' if request.POST.get('theme') == 'dark' else 'light', max_age=365*86400, samesite='Lax', secure=request.is_secure())
    return response


def page(request, queryset):
    return Paginator(queryset, 25).get_page(request.GET.get('page'))


def add_errors(form, error):
    if isinstance(error, IntegrityError):
        form.add_error(None, 'Já existe um registro com estes dados. Atualize a página e tente novamente.')
    else:
        for message in error.messages:
            form.add_error(None, message)


@roles(User.Role.ADMIN)
def dashboard(request):
    period = 'week' if request.GET.get('period') == 'week' else 'month'
    trunc = TruncWeek if period == 'week' else TruncMonth
    series = list(Sale.objects.annotate(period=trunc('sold_at', tzinfo=ZoneInfo(settings.TIME_ZONE))).values('period').annotate(total=Sum('amount'), units=Count('pk')).order_by('period'))
    totals = Sale.objects.aggregate(total=Sum('amount'), units=Count('pk'))
    models = Sale.objects.values('vehicle__model').annotate(count=Count('pk')).order_by('-count', 'vehicle__model')[:5]
    last_budget = Budget.objects.filter(order_id=OuterRef('pk')).order_by('-version').values('pk')[:1]
    completed = WorkOrder.objects.filter(status__in=[WorkOrder.Status.READY, WorkOrder.Status.CLOSED]).annotate(last=Subquery(last_budget)).values('last')
    services_rank = BudgetItem.objects.filter(budget_id__in=Subquery(completed), budget__decision=Budget.Decision.APPROVED, kind=BudgetItem.Kind.SERVICE).values('description').annotate(count=Sum('quantity')).order_by('-count', 'description')[:5]
    opened = WorkOrder.objects.exclude(status__in=[WorkOrder.Status.CLOSED, WorkOrder.Status.CANCELLED])
    return render(request, 'erp/dashboard.html', {
        'section': 'dashboard', 'title': 'Visão geral', 'period': period,
        'sales_total': totals['total'] or Decimal('0.00'), 'sales_count': totals['units'],
        'available': Vehicle.objects.filter(origin='stock', status='available').count(), 'open_orders': opened.count(),
        'series': series, 'max_total': max((r['total'] for r in series), default=Decimal('1')) or Decimal('1'),
        'model_rank': models, 'service_rank': services_rank,
        'recent_orders': WorkOrder.objects.select_related('customer', 'vehicle')[:5],
        'stages': opened.values('status').annotate(count=Count('pk')).order_by('status'),
    })


@roles(User.Role.SELLER)
def vehicles(request):
    qs = Vehicle.objects.all()
    if not request.user.is_administrative:
        qs = qs.filter(origin='stock', status='available')
    q, condition, status = (request.GET.get(k, '') for k in ['q', 'condition', 'status'])
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(model__icontains=q) | Q(color__icontains=q))
    if condition in dict(Vehicle.Condition.choices):
        qs = qs.filter(condition=condition)
    if request.user.is_administrative and status in dict(Vehicle.Status.choices):
        qs = qs.filter(status=status)
    return render(request, 'erp/vehicles.html', {'section': 'stock', 'title': 'Estoque de motos', 'page': page(request, qs), 'q': q, 'condition': condition, 'status': status})


@roles(User.Role.ADMIN)
def vehicle_create(request):
    form = forms.VehicleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            vehicle = services.create_vehicle(request.user, form.cleaned_data)
            messages.success(request, 'Veículo cadastrado.')
            return redirect('vehicle_detail', pk=vehicle.pk)
        except (ValidationError, IntegrityError) as error:
            add_errors(form, error)
    return render(request, 'erp/form.html', {'section': 'stock', 'title': 'Entrada de veículo', 'description': 'Novo/seminovo e disponibilidade são informações independentes.', 'form': form, 'submit': 'Cadastrar veículo', 'back': 'vehicles'})


@roles(User.Role.SELLER)
def vehicle_detail(request, pk):
    qs = Vehicle.objects.all()
    if not request.user.is_administrative:
        qs = qs.filter(origin='stock', status='available')
    vehicle = get_object_or_404(qs, pk=pk)
    acquisition = Acquisition.objects.filter(vehicle=vehicle).first() if request.user.is_administrative else None
    return render(request, 'erp/vehicle_detail.html', {'section': 'stock', 'title': vehicle.model, 'vehicle': vehicle, 'acquisition': acquisition})


@roles(User.Role.ADMIN)
def acquisition_detail(request, pk):
    acquisition = get_object_or_404(Acquisition.objects.select_related('vehicle'), vehicle_id=pk)
    return render(request, 'erp/acquisition.html', {'section': 'stock', 'title': 'Aquisição · administrativo', 'acquisition': acquisition})


@roles(User.Role.SELLER)
def sale_create(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if not request.user.is_administrative and (vehicle.origin != 'stock' or vehicle.status != 'available'):
        raise PermissionDenied('Moto indisponível para venda.')
    form = forms.SaleForm(request.POST or None, initial={'amount': vehicle.price})
    if request.method == 'POST' and form.is_valid():
        try:
            services.sell_vehicle(request.user, pk, **form.cleaned_data)
            messages.success(request, 'Venda confirmada. A unidade foi marcada como vendida.')
            return redirect('vehicles')
        except (ValidationError, IntegrityError) as error:
            add_errors(form, error)
    return render(request, 'erp/form.html', {'section': 'stock', 'title': 'Registrar venda', 'description': str(vehicle), 'form': form, 'submit': 'Confirmar venda', 'back': 'vehicles'})


@roles(User.Role.SELLER)
def customers(request):
    q = request.GET.get('q', '')
    qs = Customer.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(contact__icontains=q))
    return render(request, 'erp/customers.html', {'section': 'customers', 'title': 'Clientes', 'page': page(request, qs), 'q': q})


@roles(User.Role.SELLER)
def customer_create(request):
    form = forms.CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer = services.create_customer(request.user, form.cleaned_data)
        messages.success(request, 'Cliente cadastrado.')
        return redirect('customer_detail', pk=customer.pk)
    return render(request, 'erp/form.html', {'section': 'customers', 'title': 'Novo cliente', 'description': 'Cadastre o cliente para vincular vendas e atendimentos.', 'form': form, 'submit': 'Cadastrar cliente', 'back': 'customers'})


@roles(User.Role.SELLER)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'erp/customer_detail.html', {'section': 'customers', 'title': customer.name, 'customer': customer, 'sales': customer.sales.select_related('vehicle'), 'orders': customer.work_orders.select_related('vehicle')})


@roles(User.Role.SELLER, User.Role.MECHANIC)
def orders(request):
    qs = WorkOrder.objects.select_related('customer', 'vehicle')
    if not request.user.is_administrative and request.user.role == User.Role.MECHANIC:
        qs = qs.filter(mechanic=request.user)
    q, status = request.GET.get('q', ''), request.GET.get('status', '')
    if q:
        query = Q(customer__name__icontains=q) | Q(vehicle__model__icontains=q) | Q(vehicle__code__icontains=q)
        if q.isdigit():
            query |= Q(pk=int(q))
        qs = qs.filter(query)
    if status in dict(WorkOrder.Status.choices):
        qs = qs.filter(status=status)
    return render(request, 'erp/orders.html', {'section': 'workshop', 'title': 'Oficina', 'page': page(request, qs), 'q': q, 'status': status, 'statuses': WorkOrder.Status.choices})


@roles(User.Role.SELLER)
def order_create(request):
    form = forms.OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            order = services.create_order(request.user, form.cleaned_data)
            messages.success(request, 'Ordem de serviço aberta.')
            return redirect('order_detail', pk=order.pk)
        except ValidationError as error:
            add_errors(form, error)
    return render(request, 'erp/form.html', {'section': 'workshop', 'title': 'Abrir ordem de serviço', 'description': 'Vincule o cliente, a moto e o responsável pelo atendimento.', 'form': form, 'submit': 'Abrir OS', 'back': 'orders'})


@roles(User.Role.SELLER, User.Role.MECHANIC)
def order_detail(request, pk):
    order = get_object_or_404(WorkOrder.objects.select_related('vehicle', 'customer', 'mechanic'), pk=pk)
    services.order_access(request.user, order)
    technical = request.user.is_administrative or request.user.role == User.Role.MECHANIC
    budget = services.latest_budget(order)
    part_items = list(budget.items.filter(kind='part')) if budget else []
    checklist = []
    for item in order.checklist['items']:
        editable = technical and ((item['stage'] == 'entry' and order.status == 'open') or (item['stage'] == 'exit' and order.status == 'in_progress'))
        checklist.append({'item': item, 'editable': editable, 'form': forms.ChecklistForm(initial={'item_id': item['id'], 'answer': item.get('answer'), 'note': item.get('note')}, prefix=item['id'])})
    parts_form = forms.PartsForm(part_items)
    for used in order.used_parts.all():
        if f'part_{used.item_id}' in parts_form.fields:
            parts_form.fields[f'part_{used.item_id}'].initial = used.quantity
    return render(request, 'erp/order_detail.html', {'section': 'workshop', 'title': f'Ordem de serviço #{pk}', 'order': order,
        'technical': technical, 'budget': budget, 'checklist': checklist, 'part_items': part_items, 'parts_form': parts_form,
        'diagnosis_form': forms.DiagnosisForm(initial={'diagnosis': order.diagnosis}),
        'decision_form': forms.DecisionForm(initial={'version': budget.version if budget else 1, 'client_name': order.customer.name}),
        'budgets': order.budgets.all(), 'used_parts': order.used_parts.select_related('item'),
    })


@roles(User.Role.SELLER)
def budget_create(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    services.order_access(request.user, order)
    Formset = formset_factory(forms.BudgetItemForm, extra=0, min_num=1, max_num=100, validate_min=True, validate_max=True, can_delete=True)
    if request.method == 'POST':
        formset = Formset(request.POST)
        if formset.is_valid():
            items = [{k: v for k, v in f.cleaned_data.items() if k != 'DELETE'} for f in formset if f.cleaned_data and not f.cleaned_data.get('DELETE')]
            try:
                services.create_budget(request.user, pk, items)
                messages.success(request, 'Orçamento criado. Registre a aprovação antes da execução.')
                return redirect('order_detail', pk=pk)
            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))
    else:
        try:
            count = max(1, min(20, int(request.GET.get('items', '3'))))
        except ValueError:
            count = 3
        formset = Formset(initial=[{'kind': 'service', 'quantity': 1}] + [{} for _ in range(count - 1)])
    return render(request, 'erp/budget_form.html', {'section': 'workshop', 'title': f'Orçamento · OS #{pk}', 'order': order, 'formset': formset})


@require_POST
@roles(User.Role.SELLER, User.Role.MECHANIC)
def order_action(request, pk, action):
    order = get_object_or_404(WorkOrder, pk=pk)
    services.order_access(request.user, order)
    form = None
    try:
        if action == 'diagnosis':
            services.allow(request.user, User.Role.MECHANIC)
            form = forms.DiagnosisForm(request.POST)
            if form.is_valid():
                services.diagnose(request.user, pk, **form.cleaned_data)
        elif action == 'checklist':
            services.allow(request.user, User.Role.MECHANIC)
            prefix = request.POST.get('prefix', '')
            if prefix not in {i['id'] for i in order.checklist['items']}:
                raise ValidationError('Item inválido.')
            form = forms.ChecklistForm(request.POST, prefix=prefix)
            if form.is_valid():
                services.answer_checklist(request.user, pk, **form.cleaned_data)
        elif action == 'decision':
            services.allow(request.user, User.Role.SELLER)
            form = forms.DecisionForm(request.POST)
            if form.is_valid():
                services.decide_budget(request.user, pk, **form.cleaned_data)
        elif action == 'transition':
            form = forms.TransitionForm(request.POST)
            if form.is_valid():
                services.transition_order(request.user, pk, **form.cleaned_data)
        elif action == 'parts':
            services.allow(request.user, User.Role.MECHANIC)
            budget = services.latest_budget(order)
            form = forms.PartsForm(list(budget.items.filter(kind='part')) if budget else [], request.POST)
            if form.is_valid():
                services.register_parts(request.user, pk, form.usages())
        else:
            raise PermissionDenied('Operação não disponível.')
        if form is not None and form.is_valid():
            messages.success(request, 'Atendimento atualizado.')
        elif form is not None:
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
    except (ValidationError, IntegrityError) as error:
        messages.error(request, ' '.join(error.messages) if isinstance(error, ValidationError) else 'Conflito de atualização. Consulte o estado atual.')
    return redirect('order_detail', pk=pk)
