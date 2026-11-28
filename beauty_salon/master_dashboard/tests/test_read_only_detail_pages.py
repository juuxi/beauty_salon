from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.materials.models import Material
from api.models import ClassifierNode, Service, ServiceComponent, StandardNode
from api.technological_routes.models import (
    OperationComponent,
    Profession,
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
)


class ReadOnlyDetailPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username='detail-viewer',
            is_staff=True,
        )
        cls.classifier = ClassifierNode.objects.create(name='Класс')
        cls.standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=cls.classifier,
        )
        cls.service = Service.objects.create(
            name='Нетиповая услуга',
            base_class=cls.standard_node,
            is_variant=False,
            cost=100,
        )
        cls.material = Material.objects.create(name='Материал')
        cls.other_material = Material.objects.create(name='Другой материал')
        cls.profession = Profession.objects.create(name='Профессия')
        cls.operation = TechnologicalOperation.objects.create(
            name='Операция маршрута',
            profession=cls.profession,
            time=15,
            time_unit=None,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_service_components_page_shows_inherited_and_own_components_read_only(self):
        ServiceComponent.objects.create(
            standard_node=self.standard_node,
            component_material=self.material,
            amount=2,
        )
        ServiceComponent.objects.create(
            service=self.service,
            component_material=self.other_material,
            amount=3,
        )

        response = self.client.get(
            reverse(
                'master_dashboard:service_components',
                args=[self.service.pk],
            )
        )

        self.assertContains(response, self.material.name)
        self.assertContains(response, self.other_material.name)
        self.assertContains(response, 'Типовая услуга')
        self.assertNotContains(response, 'btn-edit')
        self.assertNotContains(response, 'btn-delete')

    def test_standard_node_components_page_is_read_only(self):
        ServiceComponent.objects.create(
            standard_node=self.standard_node,
            component_material=self.material,
            amount=2,
        )

        response = self.client.get(
            reverse(
                'master_dashboard:standard_node_components',
                args=[self.standard_node.pk],
            )
        )

        self.assertContains(response, self.material.name)
        self.assertNotContains(response, 'btn-edit')
        self.assertNotContains(response, 'btn-delete')

    def test_operation_details_page_shows_components_read_only(self):
        OperationComponent.objects.create(
            operation=self.operation,
            component_material=self.material,
            amount=4,
        )

        response = self.client.get(
            reverse(
                'master_dashboard:technological_operation-details',
                args=[self.operation.pk],
            )
        )

        self.assertContains(response, self.operation.name)
        self.assertContains(response, self.material.name)
        self.assertNotContains(response, 'btn-edit')
        self.assertNotContains(response, 'btn-delete')

    def test_route_operations_page_shows_ordered_operations_read_only(self):
        route = TypicalTechnologicalRoute.objects.create(
            name='Маршрут',
            standard_node=self.standard_node,
        )
        earlier_operation = TechnologicalOperation.objects.create(
            name='Операция раньше по маршруту',
            profession=self.profession,
            time=10,
            time_unit=None,
        )
        TypicalTechnologicalRouteOperation.objects.create(
            typical_technological_route=route,
            technological_operation=self.operation,
            num=2,
        )
        TypicalTechnologicalRouteOperation.objects.create(
            typical_technological_route=route,
            technological_operation=earlier_operation,
            num=1,
        )

        response = self.client.get(
            reverse(
                'master_dashboard:typical_route_operations',
                args=[self.standard_node.pk, route.pk],
            )
        )

        self.assertContains(response, route.name)
        self.assertContains(response, self.operation.name)
        self.assertContains(response, 'Просмотр операции')
        self.assertLess(
            response.content.index(earlier_operation.name.encode()),
            response.content.index(self.operation.name.encode()),
        )
        self.assertNotContains(response, 'btn-edit')
        self.assertNotContains(response, 'btn-delete')
