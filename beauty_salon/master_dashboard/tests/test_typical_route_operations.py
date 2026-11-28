from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.models import ClassifierNode, StandardNode
from api.technological_routes.models import (
    Profession,
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
)


class TypicalRouteOperationEditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username='route-editor',
            password='testpass123',
            is_staff=True,
        )
        classifier = ClassifierNode.objects.create(name='Класс')
        cls.standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=classifier,
        )
        profession = Profession.objects.create(name='Профессия')
        cls.first_operation = TechnologicalOperation.objects.create(
            name='Первая операция',
            profession=profession,
            time=10,
            time_unit=None,
        )
        cls.second_operation = TechnologicalOperation.objects.create(
            name='Вторая операция',
            profession=profession,
            time=15,
            time_unit=None,
        )
        cls.route = TypicalTechnologicalRoute.objects.create(
            name='Маршрут',
            standard_node=cls.standard_node,
        )
        cls.route_operation = TypicalTechnologicalRouteOperation.objects.create(
            typical_technological_route=cls.route,
            technological_operation=cls.first_operation,
            num=1,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_edit_route_operation(self):
        url = reverse(
            'master_dashboard:typical_route-edit',
            args=[self.standard_node.pk, self.route.pk],
        )
        response = self.client.post(
            url,
            {
                'name': 'Маршрут обновлён',
                'operations-TOTAL_FORMS': '2',
                'operations-INITIAL_FORMS': '1',
                'operations-MIN_NUM_FORMS': '0',
                'operations-MAX_NUM_FORMS': '1000',
                'operations-0-id': str(self.route_operation.pk),
                'operations-0-technological_operation': str(self.second_operation.pk),
                'operations-0-num': '1',
                'operations-1-id': '',
                'operations-1-technological_operation': '',
                'operations-1-num': '',
            },
        )

        self.assertRedirects(
            response,
            reverse(
                'master_dashboard:typical_routes',
                args=[self.standard_node.pk],
            ),
        )
        self.route.refresh_from_db()
        self.assertEqual(self.route.name, 'Маршрут обновлён')
        self.assertEqual(
            list(
                self.route.operations.values_list(
                    'technological_operation_id',
                    flat=True,
                )
            ),
            [self.second_operation.pk],
        )
