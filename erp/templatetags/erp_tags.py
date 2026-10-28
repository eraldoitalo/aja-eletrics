from decimal import Decimal, InvalidOperation
from django import template
from django.utils.formats import number_format
from erp.models import WorkOrder
register = template.Library()

@register.filter
def money(value):
    if value is None:
        return '—'
    try:
        return 'R$ ' + number_format(Decimal(value), decimal_pos=2, force_grouping=True)
    except (InvalidOperation, TypeError):
        return '—'

@register.filter
def initials(value):
    return ''.join(part[0] for part in str(value).split()[:2]).upper()

@register.filter
def stage_name(value):
    return dict(WorkOrder.Status.choices).get(value, value)

@register.filter
def answer_name(value):
    return {'ok': 'Conforme', 'issue': 'Não conforme', 'na': 'Não se aplica'}.get(value, 'Pendente')
