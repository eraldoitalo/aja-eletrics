from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Informe o email.')
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, role='admin')
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrativo'
        SELLER = 'seller', 'Vendedor'
        MECHANIC = 'mechanic', 'Mecânico'
    username = None
    email = models.EmailField('email', unique=True)
    role = models.CharField('perfil', max_length=12, choices=Role.choices, default=Role.SELLER)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    @property
    def is_administrative(self):
        return self.is_active and (self.role == self.Role.ADMIN or self.is_superuser)

    @property
    def display_name(self):
        return self.get_full_name() or self.email


class LoginThrottle(models.Model):
    key = models.CharField(primary_key=True, max_length=64)
    failures = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now)


class Customer(models.Model):
    name = models.CharField('nome', max_length=150)
    contact = models.CharField('contato', max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name', 'pk']
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', 'Novo'
        USED = 'used', 'Seminovo'
    class Origin(models.TextChoices):
        STOCK = 'stock', 'Estoque para venda'
        EXTERNAL = 'external', 'Moto externa de oficina'
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        SOLD = 'sold', 'Vendida'
        WORKSHOP = 'workshop', 'Moto externa'
    code = models.CharField('código da unidade', max_length=80, unique=True)
    model = models.CharField('modelo', max_length=120)
    color = models.CharField('cor', max_length=80)
    year = models.PositiveIntegerField('ano', validators=[MinValueValidator(1900), MaxValueValidator(2200)])
    km = models.PositiveIntegerField('quilometragem', default=0)
    condition = models.CharField('condição', max_length=8, choices=Condition.choices)
    origin = models.CharField('origem', max_length=8, choices=Origin.choices)
    status = models.CharField('situação comercial', max_length=12, choices=Status.choices)
    price = models.DecimalField('preço anunciado (R$)', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField('descrição técnica e observações comerciais', max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name='vehicle_nonnegative_price'),
            models.CheckConstraint(condition=(models.Q(origin='stock', status__in=['available', 'sold']) | models.Q(origin='external', status='workshop')), name='vehicle_origin_status'),
            models.CheckConstraint(condition=models.Q(condition__in=['new', 'used']), name='vehicle_condition_valid'),
        ]
    def __str__(self):
        return f'{self.code} · {self.model} · {self.color}'


class Acquisition(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.PROTECT, related_name='acquisition')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(purchase_price__gte=0), name='acquisition_nonnegative_cost')]


class Sale(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.PROTECT, related_name='sale')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales')
    seller = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField('valor efetivo da venda (R$)', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    sold_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-sold_at']
        constraints = [models.CheckConstraint(condition=models.Q(amount__gte=0), name='sale_nonnegative_amount')]


def initial_checklist():
    return {'template': 'recepcao-entrega', 'version': 1, 'items': [
        {'id': 'request', 'stage': 'entry', 'label': 'Solicitação do cliente registrada', 'required': True, 'answer': '', 'note': ''},
        {'id': 'condition', 'stage': 'entry', 'label': 'Condição de recebimento registrada', 'required': True, 'answer': '', 'note': ''},
        {'id': 'review', 'stage': 'exit', 'label': 'Serviços executados conferidos pelo responsável', 'required': True, 'answer': '', 'note': ''},
    ]}


class WorkOrder(models.Model):
    class Kind(models.TextChoices):
        MAINTENANCE = 'maintenance', 'Manutenção'
        REVISION = 'revision', 'Revisão'
        WARRANTY = 'warranty', 'Solicitação de garantia'
    class Status(models.TextChoices):
        OPEN = 'open', 'Aberta'
        AWAITING = 'awaiting_approval', 'Aguardando aprovação'
        AUTHORIZED = 'authorized', 'Autorizada'
        PROGRESS = 'in_progress', 'Em execução'
        READY = 'ready', 'Pronta para retirada'
        CLOSED = 'closed', 'Encerrada'
        CANCELLED = 'cancelled', 'Cancelada'
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='work_orders')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='work_orders')
    mechanic = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='assigned_orders', limit_choices_to={'role': User.Role.MECHANIC})
    complaint = models.TextField('solicitação do cliente', max_length=4000)
    diagnosis = models.TextField('diagnóstico', max_length=4000, blank=True)
    kind = models.CharField('tipo de atendimento', max_length=16, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    checklist = models.JSONField(default=initial_checklist)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ['-created_at', '-pk']


class Budget(models.Model):
    class Decision(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        APPROVED = 'approved', 'Aprovado'
        REJECTED = 'rejected', 'Recusado'
    order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name='budgets')
    version = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=14, decimal_places=2)
    decision = models.CharField(max_length=10, choices=Decision.choices, default=Decision.PENDING)
    client_name = models.CharField('cliente ou representante', max_length=150, blank=True)
    channel = models.CharField('canal de aprovação', max_length=120, blank=True)
    evidence = models.TextField('referência da comprovação', max_length=2000, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='budget_decisions')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_budgets')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['version']
        constraints = [models.UniqueConstraint(fields=['order', 'version'], name='budget_unique_version'), models.CheckConstraint(condition=models.Q(total__gte=0), name='budget_nonnegative_total')]


class BudgetItem(models.Model):
    class Kind(models.TextChoices):
        SERVICE = 'service', 'Serviço'
        PART = 'part', 'Peça'
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    kind = models.CharField('tipo', max_length=8, choices=Kind.choices)
    description = models.CharField('descrição', max_length=300)
    quantity = models.PositiveIntegerField('quantidade', validators=[MinValueValidator(1), MaxValueValidator(10000)])
    unit_price = models.DecimalField('valor unitário (R$)', max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    class Meta:
        ordering = ['pk']
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gte=1, unit_price__gte=0), name='budget_item_valid_values')]
    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class PartUsage(models.Model):
    order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name='used_parts')
    item = models.ForeignKey(BudgetItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['order', 'item'], name='part_usage_unique')]


class Audit(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=60)
    entity = models.CharField(max_length=30)
    entity_id = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
