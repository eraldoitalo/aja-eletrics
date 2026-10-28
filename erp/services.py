"""Regras de negócio e transações; todas as mutações passam por esta camada."""
from copy import deepcopy
from decimal import Decimal
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Acquisition, Audit, Budget, BudgetItem, Customer, PartUsage, Sale, User, Vehicle, WorkOrder


def allow(actor, *roles):
    if not actor.is_authenticated or not actor.is_active or not (actor.is_administrative or actor.role in roles):
        raise PermissionDenied('Você não tem permissão para esta operação.')


def audit(actor, action, entity):
    Audit.objects.create(actor=actor, action=action, entity=entity._meta.model_name, entity_id=entity.pk)


def order_access(actor, order):
    allow(actor, User.Role.SELLER, User.Role.MECHANIC)
    if not actor.is_administrative and actor.role == User.Role.MECHANIC and order.mechanic_id != actor.pk:
        raise PermissionDenied('Atendimento não atribuído a este mecânico.')


def locked_order(actor, pk):
    order = WorkOrder.objects.select_for_update().get(pk=pk)
    order_access(actor, order)
    if order.status in [WorkOrder.Status.CLOSED, WorkOrder.Status.CANCELLED]:
        raise ValidationError('Esta ordem de serviço já está encerrada ou cancelada.')
    return order


def latest_budget(order):
    return order.budgets.order_by('-version').first()


@transaction.atomic
def create_customer(actor, cleaned):
    allow(actor, User.Role.SELLER)
    customer = Customer(**cleaned)
    customer.full_clean()
    customer.save()
    audit(actor, 'customer.created', customer)
    return customer


@transaction.atomic
def create_vehicle(actor, cleaned):
    allow(actor, User.Role.ADMIN)
    data = dict(cleaned)
    cost = data.pop('purchase_price', None)
    vehicle = Vehicle(**data)
    vehicle.status = Vehicle.Status.AVAILABLE if vehicle.origin == Vehicle.Origin.STOCK else Vehicle.Status.WORKSHOP
    vehicle.full_clean()
    vehicle.save()
    if vehicle.origin == Vehicle.Origin.STOCK:
        if cost is None:
            raise ValidationError('Informe o custo de aquisição para entrada no estoque.')
        acquisition = Acquisition(vehicle=vehicle, purchase_price=cost)
        acquisition.full_clean()
        acquisition.save()
    audit(actor, 'vehicle.created', vehicle)
    return vehicle


@transaction.atomic
def sell_vehicle(actor, pk, customer, amount):
    allow(actor, User.Role.SELLER)
    vehicle = Vehicle.objects.select_for_update().get(pk=pk)
    if vehicle.origin != Vehicle.Origin.STOCK or vehicle.status != Vehicle.Status.AVAILABLE:
        raise ValidationError('Esta moto não está disponível para venda.')
    sale = Sale(vehicle=vehicle, customer=customer, seller=actor, amount=amount)
    sale.full_clean()
    sale.save()
    vehicle.status = Vehicle.Status.SOLD
    vehicle.save(update_fields=['status'])
    audit(actor, 'sale.created', sale)
    return sale


@transaction.atomic
def create_order(actor, cleaned):
    allow(actor, User.Role.SELLER)
    order = WorkOrder(**cleaned)
    if order.mechanic and (order.mechanic.role != User.Role.MECHANIC or not order.mechanic.is_active):
        raise ValidationError('Selecione um mecânico ativo.')
    order.full_clean()
    order.save()
    audit(actor, 'order.created', order)
    return order


@transaction.atomic
def diagnose(actor, pk, diagnosis):
    allow(actor, User.Role.MECHANIC)
    order = locked_order(actor, pk)
    if order.status != WorkOrder.Status.OPEN:
        raise ValidationError('O diagnóstico inicial já foi finalizado.')
    if not diagnosis.strip():
        raise ValidationError('Descreva o diagnóstico.')
    order.diagnosis = diagnosis.strip()
    order.full_clean()
    order.save(update_fields=['diagnosis'])
    audit(actor, 'order.diagnosis', order)


@transaction.atomic
def answer_checklist(actor, pk, item_id, answer, note):
    allow(actor, User.Role.MECHANIC)
    order = locked_order(actor, pk)
    checklist = deepcopy(order.checklist)
    item = next((i for i in checklist['items'] if i['id'] == item_id), None)
    if not item or answer not in ['ok', 'issue', 'na']:
        raise ValidationError('Item ou resposta inválida.')
    if (item['stage'] == 'entry' and order.status != WorkOrder.Status.OPEN) or (item['stage'] == 'exit' and order.status != WorkOrder.Status.PROGRESS):
        raise ValidationError('O checklist não pode ser alterado nesta etapa.')
    if answer != 'ok' and not note.strip():
        raise ValidationError('Informe a justificativa para esta resposta.')
    item.update(answer=answer, note=note.strip(), answered_by=actor.pk, answered_at=timezone.now().isoformat())
    order.checklist = checklist
    order.save(update_fields=['checklist'])
    audit(actor, 'order.checklist', order)


@transaction.atomic
def create_budget(actor, pk, items):
    allow(actor, User.Role.SELLER)
    order = locked_order(actor, pk)
    if order.status not in [WorkOrder.Status.OPEN, WorkOrder.Status.AWAITING, WorkOrder.Status.AUTHORIZED]:
        raise ValidationError('Após iniciar, novos serviços devem ser registrados em OS complementar nesta versão.')
    if not order.diagnosis.strip() or any(not i.get('answer') for i in order.checklist['items'] if i['stage'] == 'entry'):
        raise ValidationError('Conclua o checklist de entrada e o diagnóstico antes do orçamento.')
    if not 1 <= len(items) <= 100 or not any(i['kind'] == BudgetItem.Kind.SERVICE for i in items):
        raise ValidationError('Informe de 1 a 100 itens, incluindo pelo menos um serviço.')
    previous = latest_budget(order)
    total = sum((i['quantity'] * i['unit_price'] for i in items), Decimal('0.00'))
    budget = Budget(order=order, version=previous.version + 1 if previous else 1, total=total, created_by=actor)
    budget.full_clean()
    budget.save()
    for data in items:
        item = BudgetItem(budget=budget, **data)
        item.full_clean()
        item.save()
    order.status = WorkOrder.Status.AWAITING
    order.save(update_fields=['status'])
    audit(actor, 'budget.created', budget)
    return budget


@transaction.atomic
def decide_budget(actor, pk, version, decision, client_name, channel, evidence):
    allow(actor, User.Role.SELLER)
    order = locked_order(actor, pk)
    budget = latest_budget(order)
    if order.status != WorkOrder.Status.AWAITING or not budget or budget.decision != Budget.Decision.PENDING:
        raise ValidationError('Não há orçamento pendente de decisão.')
    if budget.version != version:
        raise ValidationError('O orçamento foi revisado. Consulte a versão atual antes de aprovar.')
    if decision not in [Budget.Decision.APPROVED, Budget.Decision.REJECTED] or not all(v.strip() for v in [client_name, channel, evidence]):
        raise ValidationError('Informe a decisão, o cliente, o canal e a referência da comprovação.')
    budget.decision, budget.client_name, budget.channel, budget.evidence = decision, client_name.strip(), channel.strip(), evidence.strip()
    budget.decided_at, budget.decided_by = timezone.now(), actor
    budget.full_clean()
    budget.save()
    order.status = WorkOrder.Status.AUTHORIZED if decision == Budget.Decision.APPROVED else WorkOrder.Status.AWAITING
    order.save(update_fields=['status'])
    audit(actor, 'budget.decision', budget)


@transaction.atomic
def transition_order(actor, pk, target, reason=''):
    order = locked_order(actor, pk)
    if target == WorkOrder.Status.CANCELLED:
        allow(actor, User.Role.ADMIN)
        if not reason.strip():
            raise ValidationError('Informe o motivo do cancelamento.')
        order.cancellation_reason = reason.strip()
    elif order.status == WorkOrder.Status.AUTHORIZED and target == WorkOrder.Status.PROGRESS:
        allow(actor, User.Role.MECHANIC)
        budget = latest_budget(order)
        if not budget or budget.decision != Budget.Decision.APPROVED:
            raise ValidationError('É necessária a aprovação da versão atual do orçamento.')
    elif order.status == WorkOrder.Status.PROGRESS and target == WorkOrder.Status.READY:
        allow(actor, User.Role.MECHANIC)
        if any(i['required'] and i.get('answer') != 'ok' for i in order.checklist['items']):
            raise ValidationError('Resolva os itens obrigatórios do checklist antes de concluir.')
    elif order.status == WorkOrder.Status.READY and target == WorkOrder.Status.CLOSED:
        allow(actor, User.Role.SELLER)
        order.closed_at = timezone.now()
    else:
        raise ValidationError('Transição de etapa inválida.')
    order.status = target
    order.save(update_fields=['status', 'closed_at', 'cancellation_reason'])
    audit(actor, 'order.transition', order)


@transaction.atomic
def register_parts(actor, pk, usages):
    allow(actor, User.Role.MECHANIC)
    order = locked_order(actor, pk)
    if order.status != WorkOrder.Status.PROGRESS:
        raise ValidationError('As peças devem ser registradas durante a execução.')
    budget = latest_budget(order)
    if not budget or budget.decision != Budget.Decision.APPROVED:
        raise ValidationError('Orçamento aprovado não encontrado.')
    valid = {item.pk: item for item in budget.items.filter(kind=BudgetItem.Kind.PART)}
    seen = set()
    for item_id, quantity in usages:
        if item_id not in valid or item_id in seen or not isinstance(quantity, int) or not 0 <= quantity <= valid[item_id].quantity:
            raise ValidationError('Peça ou quantidade incompatível com o orçamento aprovado.')
        seen.add(item_id)
        PartUsage.objects.update_or_create(order=order, item=valid[item_id], defaults={'quantity': quantity})
    audit(actor, 'order.parts', order)
