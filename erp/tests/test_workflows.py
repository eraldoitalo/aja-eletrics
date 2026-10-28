from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from threading import Barrier
from zoneinfo import ZoneInfo
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import close_old_connections, connection, IntegrityError, transaction
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from erp import services
from erp.models import Acquisition, Budget, BudgetItem, Customer, PartUsage, Sale, User, Vehicle, WorkOrder


def make_fixture():
    admin = User.objects.create_user('admin@example.test', 'test-only-pass-2026', role='admin', first_name='Admin')
    seller = User.objects.create_user('seller@example.test', 'test-only-pass-2026', role='seller', first_name='Vendedor')
    mechanic = User.objects.create_user('mechanic@example.test', 'test-only-pass-2026', role='mechanic', first_name='Mecânico')
    other = User.objects.create_user('other@example.test', 'test-only-pass-2026', role='mechanic', first_name='Outro')
    customer = Customer.objects.create(name='Cliente de teste', contact='Contato fictício')
    vehicle = services.create_vehicle(admin, vehicle_data())
    return admin, seller, mechanic, other, customer, vehicle


def vehicle_data(**changes):
    data = {'code': 'TEST-001', 'model': 'Modelo fictício', 'color': 'Preta', 'year': 2026, 'km': 0,
        'condition': 'new', 'origin': 'stock', 'price': Decimal('11900.00'),
        'purchase_price': Decimal('8765.43'), 'description': 'Ficha técnica de teste.'}
    data.update(changes)
    return data


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class WorkflowTests(TestCase):
    def setUp(self):
        self.admin, self.seller, self.mechanic, self.other, self.customer, self.vehicle = make_fixture()
        self.client.force_login(self.admin)

    def order(self):
        return services.create_order(self.seller, {'customer': self.customer, 'vehicle': self.vehicle, 'mechanic': self.mechanic,
            'kind': 'maintenance', 'complaint': 'Relato de teste.'})

    def prepared(self):
        order = self.order()
        for item in ['request', 'condition']:
            services.answer_checklist(self.mechanic, order.pk, item, 'ok', '')
        services.diagnose(self.mechanic, order.pk, 'Diagnóstico de teste')
        return order

    def budget(self, order=None):
        order = order or self.prepared()
        budget = services.create_budget(self.seller, order.pk, [
            {'kind': 'service', 'description': 'Revisão teste', 'quantity': 1, 'unit_price': Decimal('100.00')},
            {'kind': 'part', 'description': 'Peça teste', 'quantity': 2, 'unit_price': Decimal('25.00')},
        ])
        return order, budget

    def approve(self, order, budget):
        services.decide_budget(self.seller, order.pk, budget.version, 'approved', 'Cliente', 'Presencial', 'Referência fictícia')

    def test_database_is_postgresql(self):
        self.assertEqual(connection.vendor, 'postgresql')

    def test_login_and_logout(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('vehicles')).status_code, 302)
        result = self.client.post(reverse('login'), {'username': self.admin.email, 'password': 'test-only-pass-2026'})
        self.assertRedirects(result, reverse('home'), fetch_redirect_response=False)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))

    def test_invalid_login_does_not_authenticate(self):
        self.client.logout()
        result = self.client.post(reverse('login'), {'username': self.admin.email, 'password': 'invalid'})
        self.assertEqual(result.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_rate_limit_is_shared_in_database(self):
        self.client.logout()
        for _ in range(10):
            self.client.post(reverse('login'), {'username': self.admin.email, 'password': 'incorrect'})
        other_client = Client()
        blocked = other_client.post(reverse('login'), {'username': self.admin.email, 'password': 'test-only-pass-2026'})
        self.assertEqual(blocked.status_code, 429)
        self.assertNotIn('_auth_user_id', other_client.session)

    def test_role_redirects(self):
        for user, target in [(self.admin, 'dashboard'), (self.seller, 'vehicles'), (self.mechanic, 'orders')]:
            self.client.force_login(user)
            self.assertRedirects(self.client.get(reverse('home')), reverse(target), fetch_redirect_response=False)

    def test_only_admin_creates_stock(self):
        for user in [self.seller, self.mechanic]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse('vehicle_create')).status_code, 403)
            self.assertEqual(self.client.post(reverse('vehicle_create'), vehicle_data(code='BLOCKED')).status_code, 403)
            with self.assertRaises(PermissionDenied):
                services.create_vehicle(user, vehicle_data(code='BLOCKED'))
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_admin_entry_form_writes_acquisition(self):
        data = vehicle_data(code='FORM-001', price='12.000,00', purchase_price='9.000,00')
        response = self.client.post(reverse('vehicle_create'), data)
        self.assertEqual(response.status_code, 302, response.context['form'].errors if response.status_code == 200 else '')
        v = Vehicle.objects.get(code='FORM-001')
        self.assertEqual(v.acquisition.purchase_price, Decimal('9000.00'))

    def test_cost_is_absent_from_seller_and_mechanic_html(self):
        self.assertContains(self.client.get(reverse('vehicle_detail', args=[self.vehicle.pk])), '8.765,43')
        self.client.force_login(self.seller)
        html = self.client.get(reverse('vehicle_detail', args=[self.vehicle.pk]))
        self.assertNotContains(html, '8.765,43')
        self.assertNotContains(html, '8765.43')
        for user in [self.seller, self.mechanic]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse('acquisition_detail', args=[self.vehicle.pk])).status_code, 403)

    def test_purchase_field_injection_is_rejected(self):
        self.client.force_login(self.seller)
        r = self.client.post(reverse('sale_create', args=[self.vehicle.pk]), {'customer': self.customer.pk, 'amount': '10000,00', 'purchase_price': '0'})
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Sale.objects.exists())

    def test_dashboard_is_admin_only(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        for user in [self.seller, self.mechanic]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse('dashboard')).status_code, 403)

    def test_external_vehicle_never_enters_commercial_stock(self):
        external = services.create_vehicle(self.admin, vehicle_data(code='EXT-1', origin='external', purchase_price=None))
        self.assertEqual(external.status, 'workshop')
        self.assertFalse(Acquisition.objects.filter(vehicle=external).exists())
        self.client.force_login(self.seller)
        self.assertNotContains(self.client.get(reverse('vehicles')), 'EXT-1')
        with self.assertRaises(ValidationError):
            services.sell_vehicle(self.seller, external.pk, self.customer, Decimal('500'))

    def test_sale_preserves_condition_and_one_sale_per_unit(self):
        services.sell_vehicle(self.seller, self.vehicle.pk, self.customer, Decimal('11000'))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'sold')
        self.assertEqual(self.vehicle.condition, 'new')
        with self.assertRaises(ValidationError):
            services.sell_vehicle(self.admin, self.vehicle.pk, self.customer, Decimal('11000'))
        self.assertEqual(Sale.objects.count(), 1)
        self.client.force_login(self.seller)
        self.assertNotContains(self.client.get(reverse('vehicles')), 'TEST-001')

    def test_negative_cost_rolls_back_vehicle(self):
        with self.assertRaises(ValidationError):
            services.create_vehicle(self.admin, vehicle_data(code='INVALID', purchase_price=Decimal('-1')))
        self.assertFalse(Vehicle.objects.filter(code='INVALID').exists())

    def test_database_blocks_duplicate_sale(self):
        services.sell_vehicle(self.seller, self.vehicle.pk, self.customer, Decimal('11000'))
        with self.assertRaises(IntegrityError), transaction.atomic():
            Sale.objects.create(vehicle=self.vehicle, customer=self.customer, seller=self.seller, amount=1)

    def test_sold_vehicle_can_receive_order_without_becoming_available(self):
        services.sell_vehicle(self.seller, self.vehicle.pk, self.customer, Decimal('11000'))
        self.order()
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'sold')

    def test_mechanic_only_sees_assigned_orders(self):
        order = self.order()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('order_detail', args=[order.pk])).status_code, 403)
        self.assertEqual(list(self.client.get(reverse('orders')).context['page']), [])
        self.client.force_login(self.mechanic)
        self.assertEqual(self.client.get(reverse('order_detail', args=[order.pk])).status_code, 200)

    def test_order_detail_never_contains_acquisition(self):
        order = self.order()
        for user in [self.mechanic, self.seller]:
            self.client.force_login(user)
            result = self.client.get(reverse('order_detail', args=[order.pk]))
            self.assertNotContains(result, '8.765,43')
            self.assertNotContains(result, '8765.43')

    def test_execution_without_approval_is_blocked(self):
        order = self.order()
        with self.assertRaises(ValidationError):
            services.transition_order(self.mechanic, order.pk, 'in_progress')
        order, _ = self.budget()
        with self.assertRaises(ValidationError):
            services.transition_order(self.mechanic, order.pk, 'in_progress')

    def test_budget_requires_entry_checklist_and_diagnosis(self):
        order = self.order()
        with self.assertRaises(ValidationError):
            services.create_budget(self.seller, order.pk, [{'kind': 'service', 'description': 'Teste', 'quantity': 1, 'unit_price': Decimal('1')}])

    def test_budget_versioning_and_stale_decision(self):
        order, first = self.budget()
        self.approve(order, first)
        second = services.create_budget(self.seller, order.pk, [{'kind': 'service', 'description': 'Novo escopo', 'quantity': 1, 'unit_price': Decimal('120')}])
        first.refresh_from_db()
        self.assertEqual(first.total, Decimal('150'))
        self.assertEqual(first.decision, 'approved')
        self.assertEqual(second.version, 2)
        self.assertEqual(second.decision, 'pending')
        with self.assertRaises(ValidationError):
            services.decide_budget(self.seller, order.pk, 1, 'approved', 'Cliente', 'Presencial', 'Referência')
        with self.assertRaises(ValidationError):
            services.transition_order(self.mechanic, order.pk, 'in_progress')

    def test_refusal_does_not_authorize_execution(self):
        order, budget = self.budget()
        services.decide_budget(self.seller, order.pk, budget.version, 'rejected', 'Cliente', 'Telefone', 'Recusa fictícia')
        with self.assertRaises(ValidationError):
            services.transition_order(self.mechanic, order.pk, 'in_progress')

    def test_complete_workflow_and_parts_without_stock(self):
        order, budget = self.budget()
        self.approve(order, budget)
        services.transition_order(self.mechanic, order.pk, 'in_progress')
        item = budget.items.get(kind='part')
        with self.assertRaises(ValidationError):
            services.register_parts(self.mechanic, order.pk, [(item.pk, 3)])
        services.register_parts(self.mechanic, order.pk, [(item.pk, 2)])
        with self.assertRaises(ValidationError):
            services.transition_order(self.mechanic, order.pk, 'ready')
        services.answer_checklist(self.mechanic, order.pk, 'review', 'ok', '')
        services.transition_order(self.mechanic, order.pk, 'ready')
        services.transition_order(self.seller, order.pk, 'closed')
        order.refresh_from_db()
        self.assertEqual(order.status, 'closed')
        self.assertEqual(order.used_parts.get().quantity, 2)
        self.assertEqual(order.checklist['version'], 1)
        with self.assertRaises(ValidationError):
            services.diagnose(self.admin, order.pk, 'Tentativa de alterar encerrada')

    def test_customer_history_is_linked_to_correct_person(self):
        order = self.order()
        other = Customer.objects.create(name='Outra pessoa', contact='Outro contato')
        first = self.client.get(reverse('customer_detail', args=[self.customer.pk]))
        second = self.client.get(reverse('customer_detail', args=[other.pk]))
        self.assertEqual(list(first.context['orders']), [order])
        self.assertEqual(list(second.context['orders']), [])

    def test_csrf_is_required_for_mutations(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.admin)
        self.assertEqual(strict.post(reverse('vehicle_create'), vehicle_data()).status_code, 403)
        self.assertEqual(strict.get(reverse('logout')).status_code, 405)

    def test_theme_does_not_allow_external_redirect(self):
        result = self.client.post(reverse('theme'), {'next': 'https://evil.example', 'theme': 'dark'})
        self.assertEqual(result.url, '/')
        self.assertEqual(result.cookies['aja_theme'].value, 'dark')

    def test_html_escapes_untrusted_description(self):
        self.vehicle.description = '<script>alert(1)</script>'
        self.vehicle.save()
        result = self.client.get(reverse('vehicle_detail', args=[self.vehicle.pk]))
        self.assertContains(result, '&lt;script&gt;')
        self.assertNotContains(result, '<script>alert(1)</script>')

    def test_dashboard_week_month_boundaries_use_sao_paulo(self):
        sale = services.sell_vehicle(self.seller, self.vehicle.pk, self.customer, Decimal('10000'))
        # 01/06 01:00 UTC ainda é domingo, 31/05 às 22h em São Paulo.
        Sale.objects.filter(pk=sale.pk).update(sold_at=datetime(2026, 6, 1, 1, tzinfo=ZoneInfo('UTC')))
        month = self.client.get(reverse('dashboard')).context
        week = self.client.get(reverse('dashboard') + '?period=week').context
        self.assertEqual(month['series'][0]['period'].date().isoformat(), '2026-05-01')
        self.assertEqual(week['series'][0]['period'].date().isoformat(), '2026-05-25')
        self.assertEqual(month['sales_total'], Decimal('10000'))

    def test_service_ranking_ignores_pending_and_old_budget_versions(self):
        order, first = self.budget()
        self.approve(order, first)
        second = services.create_budget(self.seller, order.pk, [{'kind': 'service', 'description': 'Serviço atual', 'quantity': 2, 'unit_price': Decimal('50')}])
        self.assertEqual(list(self.client.get(reverse('dashboard')).context['service_rank']), [])
        self.approve(order, second)
        services.transition_order(self.mechanic, order.pk, 'in_progress')
        services.answer_checklist(self.mechanic, order.pk, 'review', 'ok', '')
        services.transition_order(self.mechanic, order.pk, 'ready')
        rank = list(self.client.get(reverse('dashboard')).context['service_rank'])
        self.assertEqual(rank, [{'description': 'Serviço atual', 'count': 2}])

    def test_cancel_requires_administrative_and_reason(self):
        order = self.order()
        with self.assertRaises(PermissionDenied):
            services.transition_order(self.mechanic, order.pk, 'cancelled', 'Motivo')
        with self.assertRaises(ValidationError):
            services.transition_order(self.admin, order.pk, 'cancelled', '')
        services.transition_order(self.admin, order.pk, 'cancelled', 'Solicitado pelo cliente')
        order.refresh_from_db()
        self.assertEqual(order.cancellation_reason, 'Solicitado pelo cliente')

    def test_all_operational_pages_render(self):
        order = self.prepared()
        urls = [reverse(name) for name in ['dashboard', 'vehicles', 'vehicle_create', 'customers', 'customer_create', 'orders', 'order_create']]
        urls += [reverse('vehicle_detail', args=[self.vehicle.pk]), reverse('acquisition_detail', args=[self.vehicle.pk]),
            reverse('sale_create', args=[self.vehicle.pk]), reverse('customer_detail', args=[self.customer.pk]),
            reverse('order_detail', args=[order.pk]), reverse('budget_create', args=[order.pk])]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ConcurrentSaleTests(TransactionTestCase):
    def test_two_connections_cannot_sell_same_vehicle(self):
        admin, seller, _, _, customer, vehicle = make_fixture()
        barrier = Barrier(2)
        def worker(actor_id):
            close_old_connections()
            try:
                actor = User.objects.get(pk=actor_id)
                buyer = Customer.objects.get(pk=customer.pk)
                with connection.cursor() as cursor:
                    cursor.execute("SET lock_timeout = '5s'")
                barrier.wait(timeout=10)
                try:
                    services.sell_vehicle(actor, vehicle.pk, buyer, Decimal('11000'))
                    return 'sold'
                except ValidationError:
                    return 'blocked'
            finally:
                connection.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, user.pk) for user in [admin, seller]]
            outcomes = sorted(f.result(timeout=15) for f in futures)
        self.assertEqual(outcomes, ['blocked', 'sold'])
        self.assertEqual(Sale.objects.filter(vehicle=vehicle).count(), 1)
