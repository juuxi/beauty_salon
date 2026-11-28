from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.materials.models import Material
from api.models import ClassifierNode, Service, ServiceComponent, StandardNode
from api.technological_routes.models import (
    OperationComponent,
    Profession,
    TechnologicalOperation,
)


class ComponentManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username='component-editor',
            is_staff=True,
        )
        cls.classifier = ClassifierNode.objects.create(name='Класс')
        cls.standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=cls.classifier,
        )
        cls.material = Material.objects.create(name='Материал')
        cls.other_material = Material.objects.create(name='Другой материал')
        cls.component_service = Service.objects.create(
            name='Услуга-компонент',
            base_class=cls.standard_node,
            is_variant=False,
            cost=100,
        )
        cls.profession = Profession.objects.create(name='Профессия')

    def setUp(self):
        self.client.force_login(self.user)

    def component_form_data(self, rows, initial_count=0):
        data = {
            'components-TOTAL_FORMS': str(len(rows)),
            'components-INITIAL_FORMS': str(initial_count),
            'components-MIN_NUM_FORMS': '0',
            'components-MAX_NUM_FORMS': '1000',
        }
        for index, row in enumerate(rows):
            prefix = f'components-{index}-'
            data[prefix + 'component_service'] = row.get('service', '')
            data[prefix + 'component_material'] = row.get('material', '')
            data[prefix + 'amount'] = row.get('amount', '')
            if 'id' in row:
                data[prefix + 'id'] = str(row['id'])
        return data

    def test_create_pages_render_component_editors(self):
        create_urls = (
            'master_dashboard:technological_operation-create',
            'master_dashboard:standard_node-create',
            'master_dashboard:service-create',
        )
        for url_name in create_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertContains(response, 'data-add-component')

    def test_operation_can_have_service_and_material_components(self):
        data = {
            'name': 'Операция',
            'profession': str(self.profession.pk),
            'qualification': '',
            'tool': '',
            'time': '10',
            'time_unit': '',
            'parent': '',
        }
        data.update(self.component_form_data([
            {
                'service': str(self.component_service.pk),
                'amount': '2',
            },
            {
                'material': str(self.material.pk),
                'amount': '3',
            },
        ]))

        response = self.client.post(
            reverse('master_dashboard:technological_operation-create'),
            data,
        )

        self.assertRedirects(
            response,
            reverse('master_dashboard:technological_operations'),
        )
        operation = TechnologicalOperation.objects.get(name='Операция')
        self.assertEqual(
            list(
                OperationComponent.objects.filter(
                    operation=operation,
                ).values_list(
                    'component_service_id',
                    'component_material_id',
                    'amount',
                )
            ),
            [
                (self.component_service.pk, None, 2),
                (None, self.material.pk, 3),
            ],
        )

    def test_component_row_rejects_both_service_and_material(self):
        data = {
            'name': 'Операция',
            'profession': str(self.profession.pk),
            'qualification': '',
            'tool': '',
            'time': '10',
            'time_unit': '',
            'parent': '',
        }
        data.update(self.component_form_data([
            {
                'service': str(self.component_service.pk),
                'material': str(self.material.pk),
                'amount': '2',
            },
        ]))

        response = self.client.post(
            reverse('master_dashboard:technological_operation-create'),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            TechnologicalOperation.objects.filter(name='Операция').exists()
        )
        self.assertContains(
            response,
            'Выберите для компонента ровно одну услугу или один материал.',
        )

    def test_typical_service_can_have_a_material_component(self):
        data = {
            'name': 'Новая типовая услуга',
            'base_class': str(self.classifier.pk),
            'code': '',
        }
        data.update(self.component_form_data([
            {
                'material': str(self.material.pk),
                'amount': '4',
            },
        ]))

        response = self.client.post(
            reverse('master_dashboard:standard_node-create'),
            data,
        )

        self.assertRedirects(
            response,
            reverse('master_dashboard:standard_nodes'),
        )
        standard_node = StandardNode.objects.get(name='Новая типовая услуга')
        self.assertEqual(
            list(
                ServiceComponent.objects.filter(
                    standard_node=standard_node,
                ).values_list(
                    'component_material_id',
                    'amount',
                )
            ),
            [(self.material.pk, 4)],
        )

    def test_service_components_include_typical_components(self):
        ServiceComponent.objects.create(
            standard_node=self.standard_node,
            component_material=self.material,
            amount=2,
        )
        data = {
            'name': 'Нетиповая услуга',
            'base_class': str(self.standard_node.pk),
            'is_variant': '0',
            'cost': '200',
            'code': '',
        }
        data.update(self.component_form_data([
            {
                'service': str(self.component_service.pk),
                'amount': '3',
            },
        ]))

        response = self.client.post(
            reverse('master_dashboard:service-create'),
            data,
        )

        self.assertRedirects(
            response,
            reverse('master_dashboard:services'),
            fetch_redirect_response=False,
        )
        service = Service.objects.get(name='Нетиповая услуга')
        self.assertCountEqual(
            list(
                ServiceComponent.objects.filter(service=service).values_list(
                    'component_service_id',
                    'component_material_id',
                    'amount',
                )
            ),
            [
                (None, self.material.pk, 2),
                (self.component_service.pk, None, 3),
            ],
        )

    def test_service_edit_keeps_inherited_and_own_components_separate(self):
        ServiceComponent.objects.create(
            standard_node=self.standard_node,
            component_material=self.material,
            amount=2,
        )
        service = Service.objects.create(
            name='Редактируемая услуга',
            base_class=self.standard_node,
            is_variant=False,
            cost=200,
        )
        ServiceComponent.objects.create(
            service=service,
            component_material=self.material,
            amount=2,
        )
        own_component = ServiceComponent.objects.create(
            service=service,
            component_material=self.other_material,
            amount=5,
        )

        data = {
            'name': service.name,
            'base_class': str(self.standard_node.pk),
            'is_variant': '0',
            'cost': '200',
            'code': '',
        }
        data.update(self.component_form_data(
            [
                {
                    'id': own_component.pk,
                    'material': str(self.other_material.pk),
                    'amount': '5',
                },
                {},
            ],
            initial_count=1,
        ))

        response = self.client.post(
            reverse('master_dashboard:service-edit', args=[service.pk]),
            data,
        )

        self.assertRedirects(
            response,
            reverse('master_dashboard:services'),
            fetch_redirect_response=False,
        )
        self.assertCountEqual(
            list(
                service.components.values_list(
                    'component_material_id',
                    'amount',
                )
            ),
            [
                (self.material.pk, 2),
                (self.other_material.pk, 5),
            ],
        )
