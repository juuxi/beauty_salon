from decimal import Decimal
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from master_dashboard import views


class MaterialUsagePageTests(TestCase):
    def assert_material_report(
        self,
        view,
        object_id,
        object_name,
        sql,
        expected_back_url,
    ):
        entity = SimpleNamespace(pk=object_id, name=object_name)
        cursor = MagicMock()
        cursor.fetchall.return_value = [('Материал', Decimal('1.25'))]
        cursor_context = MagicMock()
        cursor_context.__enter__.return_value = cursor

        with (
            patch(
                'master_dashboard.views.get_object_or_404',
                return_value=entity,
            ),
            patch(
                'master_dashboard.views.connection.cursor',
                return_value=cursor_context,
            ),
        ):
            request = RequestFactory().get('/')
            request.user = AnonymousUser()
            response = view(request, object_id)

        cursor.execute.assert_called_once_with(sql, [object_id])
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('Материал', html)
        self.assertIn('1.25', html)
        self.assertIn(expected_back_url, html)
        self.assertNotIn('btn-edit', html)
        self.assertNotIn('btn-delete', html)

    def test_operation_material_usage_calls_mr_q(self):
        self.assert_material_report(
            views.operation_material_usage,
            12,
            'Операция',
            'SELECT material_name, total_amount FROM public.mr_q(%s)',
            reverse('master_dashboard:operation_components', args=[12]),
        )

    def test_service_material_usage_calls_calc_bom(self):
        self.assert_material_report(
            views.service_material_usage,
            23,
            'Услуга',
            'SELECT material_name, total_amount FROM public.calc_bom(%s)',
            reverse('master_dashboard:service_components', args=[23]),
        )
