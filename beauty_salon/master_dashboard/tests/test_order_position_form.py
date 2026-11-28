from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase
from django.template.loader import render_to_string

from master_dashboard.forms import OrderPositionForm


class OrderPositionFormErrorTests(SimpleTestCase):
    def test_invalid_provision_time_is_rendered(self):
        form = OrderPositionForm(
            data={
                'service': '',
                'amount': '1',
                'provision_time': '2026/10/10',
            }
        )
        self.assertFalse(form.is_valid())
        error = form.errors['provision_time'][0]
        self.assertIn('2026-10-10T14:30', error)
        form.fields['service'].choices = [('', '---------')]

        html = render_to_string(
            'order/order_position-create.html',
            {
                'form': form,
                'order': SimpleNamespace(id=1),
                'request': RequestFactory().get('/orders/1/positions/create/'),
            },
        )

        self.assertIn(error, html)
        self.assertIn('role="alert"', html)
        self.assertIn('type="datetime-local"', html)

    def test_datetime_local_value_is_accepted(self):
        field = OrderPositionForm().fields['provision_time']
        self.assertEqual(
            field.clean('2026-10-10T14:30').strftime('%Y-%m-%d %H:%M'),
            '2026-10-10 14:30',
        )
