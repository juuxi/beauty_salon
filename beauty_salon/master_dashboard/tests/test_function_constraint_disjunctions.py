from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.models import (
    ClassifierNode,
    Conjunct,
    FunctionConstraint,
    Parameter,
    ParameterNode,
    Predicate,
    StandardNode,
)


class FunctionConstraintDisjunctionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username='constraint-editor',
            password='testpass123',
            is_staff=True,
        )
        classifier = ClassifierNode.objects.create(name='Класс')
        cls.standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=classifier,
        )
        cls.first_parameter = Parameter.objects.create(
            name='Первый параметр',
            data_type='int',
        )
        cls.second_parameter = Parameter.objects.create(
            name='Второй параметр',
            data_type='int',
        )
        ParameterNode.objects.create(
            standardnode=cls.standard_node,
            parameter=cls.first_parameter,
            num=1,
        )
        ParameterNode.objects.create(
            standardnode=cls.standard_node,
            parameter=cls.second_parameter,
            num=2,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.create_url = reverse(
            'master_dashboard:function_constraint-create',
            args=[self.standard_node.pk],
        )

    def test_create_page_explains_disjunction_and_renders_add_control(self):
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дизъюнкция')
        self.assertContains(response, '+ Добавить дизъюнкт')
        self.assertContains(response, '+ Добавить конъюнкт')
        self.assertNotContains(response, 'name="conjunct"')

    def test_rejects_disjunct_without_a_conjunct(self):
        response = self.client.post(
            self.create_url,
            {
                'predicates-TOTAL_FORMS': '2',
                'predicates-INITIAL_FORMS': '0',
                'predicates-MIN_NUM_FORMS': '1',
                'predicates-MAX_NUM_FORMS': '1000',
                'predicates-0-parameter': str(self.first_parameter.pk),
                'predicates-0-operator': 'gt',
                'predicates-0-value': '10',
                'predicates-0-disjunct_number': '1',
                'predicates-1-disjunct_number': '2',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            FunctionConstraint.objects.filter(
                standard_node=self.standard_node,
            ).exists()
        )

    def test_creates_disjunction_with_multiple_disjuncts_and_conjuncts(self):
        response = self.client.post(
            self.create_url,
            {
                'predicates-TOTAL_FORMS': '3',
                'predicates-INITIAL_FORMS': '0',
                'predicates-MIN_NUM_FORMS': '1',
                'predicates-MAX_NUM_FORMS': '1000',
                'predicates-0-parameter': str(self.first_parameter.pk),
                'predicates-0-operator': 'gt',
                'predicates-0-value': '10',
                'predicates-0-disjunct_number': '1',
                'predicates-1-parameter': str(self.second_parameter.pk),
                'predicates-1-operator': 'lte',
                'predicates-1-value': '20',
                'predicates-1-disjunct_number': '1',
                'predicates-2-parameter': str(self.first_parameter.pk),
                'predicates-2-operator': 'eq',
                'predicates-2-value': '30',
                'predicates-2-disjunct_number': '2',
            },
        )

        self.assertRedirects(
            response,
            reverse(
                'master_dashboard:function_constraints',
                args=[self.standard_node.pk],
            ),
        )
        constraints = FunctionConstraint.objects.filter(
            standard_node=self.standard_node
        ).select_related('conjunct__predicate')
        self.assertEqual(constraints.count(), 3)
        disjuncts = constraints.values_list(
            'conjunct__conjunction_id',
            flat=True,
        ).distinct()
        self.assertEqual(disjuncts.count(), 2)
        self.assertEqual(
            {constraint.conjunct.predicate.value for constraint in constraints},
            {'10', '20', '30'},
        )
        list_response = self.client.get(
            reverse(
                'master_dashboard:function_constraints',
                args=[self.standard_node.pk],
            )
        )
        self.assertContains(list_response, 'Дизъюнкция')
        self.assertContains(list_response, '10')
        self.assertContains(list_response, '20')
        self.assertContains(list_response, '30')

        edit_response = self.client.post(
            self.create_url,
            {
                'predicates-TOTAL_FORMS': '3',
                'predicates-INITIAL_FORMS': '3',
                'predicates-MIN_NUM_FORMS': '1',
                'predicates-MAX_NUM_FORMS': '1000',
                'predicates-0-parameter': str(self.first_parameter.pk),
                'predicates-0-operator': 'eq',
                'predicates-0-value': '99',
                'predicates-0-disjunct_number': '1',
                'predicates-1-parameter': str(self.second_parameter.pk),
                'predicates-1-operator': 'lte',
                'predicates-1-value': '20',
                'predicates-1-disjunct_number': '1',
                'predicates-1-DELETE': 'on',
                'predicates-2-parameter': str(self.first_parameter.pk),
                'predicates-2-operator': 'eq',
                'predicates-2-value': '30',
                'predicates-2-disjunct_number': '2',
                'predicates-2-DELETE': 'on',
            },
        )

        self.assertRedirects(
            edit_response,
            reverse(
                'master_dashboard:function_constraints',
                args=[self.standard_node.pk],
            ),
        )
        updated_constraints = FunctionConstraint.objects.filter(
            standard_node=self.standard_node,
        ).select_related('conjunct__predicate')
        self.assertEqual(updated_constraints.count(), 1)
        self.assertEqual(
            updated_constraints.get().conjunct.predicate.value,
            '99',
        )

    def test_deleting_constraint_removes_all_its_disjuncts_and_predicates(self):
        predicate_ids = []
        constraints = []
        for value in ('10', '20'):
            predicate = Predicate.objects.create(
                parameter=self.first_parameter,
                operator='gt',
                value=value,
            )
            predicate_ids.append(predicate.pk)
            conjunct = Conjunct.objects.create(
                conjunction_id=900,
                predicate=predicate,
            )
            constraints.append(
                FunctionConstraint.objects.create(
                    standard_node=self.standard_node,
                    conjunct=conjunct,
                )
            )

        delete_url = reverse(
            'master_dashboard:function_constraint-delete',
            args=[self.standard_node.pk, constraints[0].pk],
        )
        response = self.client.post(delete_url)

        self.assertRedirects(
            response,
            reverse(
                'master_dashboard:function_constraints',
                args=[self.standard_node.pk],
            ),
        )
        self.assertFalse(
            FunctionConstraint.objects.filter(pk__in=[c.pk for c in constraints]).exists()
        )
        self.assertFalse(Conjunct.objects.filter(conjunction_id=900).exists())
        self.assertFalse(Predicate.objects.filter(pk__in=predicate_ids).exists())
