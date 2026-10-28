from decimal import Decimal
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Budget, BudgetItem, Customer, User, Vehicle, WorkOrder


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'username'}))


class MoneyField(forms.DecimalField):
    """Aceita 1234.56 ou 1.234,56, sem depender da localidade do navegador."""
    def __init__(self, *args, **kwargs):
        kwargs['localize'] = False
        kwargs['widget'] = forms.TextInput(attrs={'inputmode': 'decimal', 'placeholder': '0,00'})
        super().__init__(*args, **kwargs)
    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip()
            if ',' in value:
                value = value.replace('.', '').replace(',', '.')
        return super().to_python(value)
    def prepare_value(self, value):
        return format(value, 'f').replace('.', ',') if isinstance(value, Decimal) else value


class VehicleForm(forms.ModelForm):
    price = MoneyField(label='Preço anunciado (R$)', max_digits=12, decimal_places=2, min_value=0)
    purchase_price = MoneyField(label='Custo de aquisição (R$) · administrativo', max_digits=12, decimal_places=2, min_value=0, required=False)
    class Meta:
        model = Vehicle
        fields = ['code', 'model', 'color', 'year', 'km', 'condition', 'origin', 'price', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}
        localized_fields = ['price']
    def clean(self):
        cleaned = super().clean()
        if cleaned.get('origin') == Vehicle.Origin.STOCK and cleaned.get('purchase_price') is None:
            self.add_error('purchase_price', 'Informe o custo de aquisição para entrada no estoque.')
        return cleaned


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact']


class SaleForm(forms.Form):
    customer = forms.ModelChoiceField(label='Cliente', queryset=Customer.objects.all())
    amount = MoneyField(label='Valor efetivo da venda (R$)', max_digits=12, decimal_places=2, min_value=0)


class OrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['customer', 'vehicle', 'kind', 'mechanic', 'complaint']
        labels = {'customer': 'Cliente', 'vehicle': 'Moto do atendimento', 'mechanic': 'Mecânico responsável'}
        widgets = {'complaint': forms.Textarea(attrs={'rows': 4})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mechanic'].queryset = User.objects.filter(role=User.Role.MECHANIC, is_active=True).order_by('first_name', 'email')


class DiagnosisForm(forms.Form):
    diagnosis = forms.CharField(label='Constatações técnicas', max_length=4000, widget=forms.Textarea(attrs={'rows': 4}))


class ChecklistForm(forms.Form):
    item_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.ChoiceField(label='Resposta', choices=[('', 'Selecione'), ('ok', 'Conforme'), ('issue', 'Não conforme'), ('na', 'Não se aplica')])
    note = forms.CharField(label='Observação / justificativa', max_length=4000, required=False, widget=forms.Textarea(attrs={'rows': 2}))


class BudgetItemForm(forms.Form):
    kind = forms.ChoiceField(label='Tipo', choices=BudgetItem.Kind.choices)
    description = forms.CharField(label='Descrição', max_length=300)
    quantity = forms.IntegerField(label='Quantidade', min_value=1, max_value=10000, initial=1)
    unit_price = MoneyField(label='Valor unitário (R$)', min_value=0, max_digits=12, decimal_places=2)


class DecisionForm(forms.Form):
    version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    decision = forms.ChoiceField(label='Decisão do cliente', choices=[('', 'Selecione a decisão'), (Budget.Decision.APPROVED, 'Aprovado'), (Budget.Decision.REJECTED, 'Recusado')])
    client_name = forms.CharField(label='Cliente ou representante', max_length=150)
    channel = forms.CharField(label='Canal de aprovação', max_length=120)
    evidence = forms.CharField(label='Referência da comprovação', max_length=2000, widget=forms.Textarea(attrs={'rows': 3}))


class TransitionForm(forms.Form):
    target = forms.ChoiceField(choices=WorkOrder.Status.choices, widget=forms.HiddenInput)
    reason = forms.CharField(label='Motivo do cancelamento', max_length=2000, required=False)


class PartsForm(forms.Form):
    def __init__(self, items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in items:
            self.fields[f'part_{item.pk}'] = forms.IntegerField(label=f'{item.description} · aprovado: {item.quantity}', min_value=0, max_value=item.quantity, initial=0)
    def usages(self):
        return [(int(key.split('_')[1]), value) for key, value in self.cleaned_data.items()]
