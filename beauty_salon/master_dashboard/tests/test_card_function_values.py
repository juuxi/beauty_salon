from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django_filters.views import FilterView

from master_dashboard import views


class DashboardCardFunctionTests(TestCase):
    def test_service_cards_show_time_and_unit_from_tr_to(self):
        services = [SimpleNamespace(pk=4), SimpleNamespace(pk=9)]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [(30, 'минут'), (2, 'часа')]

        with (
            patch.object(
                FilterView,
                'get_context_data',
                return_value={'services': services},
            ),
            patch(
                'master_dashboard.views.connection.cursor',
            ) as cursor_factory,
        ):
            cursor_factory.return_value.__enter__.return_value = cursor
            context = views.ServiceListView().get_context_data()

        service_times = [
            (service.total_time, service.time_unit_name)
            for service in services
        ]
        self.assertEqual(service_times, [(30, 'минут'), (2, 'часа')])
        self.assertEqual(context['services'], services)
        self.assertEqual(
            cursor.execute.call_args_list[0].args[1],
            [4],
        )
        self.assertEqual(
            cursor.execute.call_args_list[1].args[1],
            [9],
        )

    def test_order_cards_show_calc_sum_for_each_order(self):
        orders = [SimpleNamespace(pk=2), SimpleNamespace(pk=6)]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [(1250,), (None,)]

        with (
            patch.object(
                views.PaginatedListView,
                'get_context_data',
                return_value={'orders': orders},
            ),
            patch(
                'master_dashboard.views.connection.cursor',
            ) as cursor_factory,
        ):
            cursor_factory.return_value.__enter__.return_value = cursor
            context = views.OrderView().get_context_data()

        self.assertEqual([order.calc_sum for order in orders], [1250, None])
        self.assertEqual(context['orders'], orders)
        self.assertEqual(
            cursor.execute.call_args_list[0].args,
            ('SELECT calc_sum(%s)', [2]),
        )
        self.assertEqual(
            cursor.execute.call_args_list[1].args,
            ('SELECT calc_sum(%s)', [6]),
        )
