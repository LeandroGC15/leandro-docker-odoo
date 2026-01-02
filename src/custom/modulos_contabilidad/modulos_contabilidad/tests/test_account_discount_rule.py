# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountDiscountRule(TransactionCase):
    """Pruebas para el modelo account.discount.rule"""

    def setUp(self):
        super().setUp()
        self.rule_model = self.env['account.discount.rule']
        self.company = self.env.company

    def test_create_discount_rule(self):
        """Test 2: Crear regla de descuento válida"""
        rule = self.rule_model.create({
            'name': 'Descuento Mayorista 10%',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
            'active': True,
        })
        self.assertEqual(rule.customer_type, 'mayorista')
        self.assertEqual(rule.discount_percentage, 10.0)
        self.assertTrue(rule.active)

    def test_discount_percentage_validation(self):
        """Verificar validación de porcentaje de descuento (0-100)"""
        # Porcentaje válido
        rule = self.rule_model.create({
            'name': 'Regla Válida',
            'customer_type': 'minorista',
            'discount_percentage': 50.0,
        })
        self.assertEqual(rule.discount_percentage, 50.0)

        # Porcentaje fuera de rango (negativo)
        with self.assertRaises(ValidationError):
            self.rule_model.create({
                'name': 'Regla Inválida Negativa',
                'customer_type': 'minorista',
                'discount_percentage': -5.0,
            })

        # Porcentaje fuera de rango (mayor a 100)
        with self.assertRaises(ValidationError):
            self.rule_model.create({
                'name': 'Regla Inválida >100',
                'customer_type': 'minorista',
                'discount_percentage': 150.0,
            })

    def test_unique_customer_type_per_company(self):
        """Verificar que no se pueden crear reglas duplicadas para el mismo tipo"""
        # Crear primera regla
        self.rule_model.create({
            'name': 'Regla Mayorista 1',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
            'active': True,
        })

        # Intentar crear segunda regla para el mismo tipo (sin fechas)
        with self.assertRaises(ValidationError):
            self.rule_model.create({
                'name': 'Regla Mayorista 2',
                'customer_type': 'mayorista',
                'discount_percentage': 15.0,
                'active': True,
            })

    def test_multiple_rules_different_types(self):
        """Verificar que se pueden crear reglas para tipos diferentes"""
        rule1 = self.rule_model.create({
            'name': 'Regla Minorista',
            'customer_type': 'minorista',
            'discount_percentage': 5.0,
        })
        rule2 = self.rule_model.create({
            'name': 'Regla Mayorista',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
        })
        rule3 = self.rule_model.create({
            'name': 'Regla VIP',
            'customer_type': 'vip',
            'discount_percentage': 15.0,
        })

        self.assertEqual(rule1.customer_type, 'minorista')
        self.assertEqual(rule2.customer_type, 'mayorista')
        self.assertEqual(rule3.customer_type, 'vip')

    def test_inactive_rule_does_not_conflict(self):
        """Verificar que reglas inactivas no causan conflictos"""
        # Crear regla activa
        rule1 = self.rule_model.create({
            'name': 'Regla Activa',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
            'active': True,
        })

        # Desactivar la regla
        rule1.active = False

        # Ahora debería poder crear otra regla para el mismo tipo
        rule2 = self.rule_model.create({
            'name': 'Nueva Regla Activa',
            'customer_type': 'mayorista',
            'discount_percentage': 12.0,
            'active': True,
        })
        self.assertTrue(rule2.active)

    def test_get_discount_for_customer_type(self):
        """Verificar método _get_discount_for_customer_type"""
        # Crear regla para mayorista
        self.rule_model.create({
            'name': 'Descuento Mayorista',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
            'active': True,
        })

        # Obtener descuento
        discount = self.rule_model._get_discount_for_customer_type('mayorista')
        self.assertEqual(discount, 10.0)

        # Tipo sin regla
        discount_none = self.rule_model._get_discount_for_customer_type('minorista')
        self.assertEqual(discount_none, 0.0)

        # Tipo 'none'
        discount_none_type = self.rule_model._get_discount_for_customer_type('none')
        self.assertEqual(discount_none_type, 0.0)

    def test_get_discount_inactive_rule(self):
        """Verificar que reglas inactivas no devuelven descuento"""
        # Crear regla inactiva
        self.rule_model.create({
            'name': 'Regla Inactiva',
            'customer_type': 'vip',
            'discount_percentage': 15.0,
            'active': False,
        })

        # No debería devolver descuento
        discount = self.rule_model._get_discount_for_customer_type('vip')
        self.assertEqual(discount, 0.0)

