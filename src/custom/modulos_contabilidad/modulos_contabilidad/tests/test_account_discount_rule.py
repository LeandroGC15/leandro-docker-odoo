# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountDiscountRule(TransactionCase):
    """Pruebas para el modelo account.discount.rule"""

    def setUp(self):
        super().setUp()
        self.rule_model = self.env['account.discount.rule']
        self.company = self.env.company

        # Buscar reglas existentes o crearlas si no existen
        self.rule_minorista = self._get_or_create_rule('minorista', 5.0)
        self.rule_mayorista = self._get_or_create_rule('mayorista', 10.0)
        self.rule_vip = self._get_or_create_rule('vip', 15.0)

    def _get_or_create_rule(self, customer_type, percentage, active=True):
        """Helper para obtener regla existente o crear nueva"""
        rule = self.rule_model.search([
            ('customer_type', '=', customer_type),
            ('company_id', '=', self.company.id),
            ('active', '=', active)
        ], limit=1)
        
        if not rule:
            rule = self.rule_model.create({
                'name': f'Test Rule {customer_type}',
                'customer_type': customer_type,
                'discount_percentage': percentage,
                'active': active,
            })
        return rule

    def test_create_discount_rule(self):
        """Test 2: Crear regla de descuento válida"""
        # Desactivamos la regla mayorista existente para poder crear una nueva en el test
        self.rule_mayorista.active = False
        
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
        # Desactivar regla minorista existente
        self.rule_minorista.active = False
        
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
        # Usamos la regla mayorista ya existente (creada en setUp/XML)
        self.assertTrue(self.rule_mayorista.active)

        # Intentar crear segunda regla para el mismo tipo
        with self.assertRaises(ValidationError):
            self.rule_model.create({
                'name': 'Regla Mayorista 2',
                'customer_type': 'mayorista',
                'discount_percentage': 15.0,
                'active': True,
            })

    def test_multiple_rules_different_types(self):
        """Verificar que se pueden crear reglas para tipos diferentes"""
        # Verificamos que las reglas creadas en setUp coexisten sin problemas
        self.assertEqual(self.rule_minorista.customer_type, 'minorista')
        self.assertEqual(self.rule_mayorista.customer_type, 'mayorista')
        self.assertEqual(self.rule_vip.customer_type, 'vip')

    def test_inactive_rule_does_not_conflict(self):
        """Verificar que reglas inactivas no causan conflictos"""
        # Usar regla mayorista existente
        rule1 = self.rule_mayorista
        
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
        # Verificar con reglas existentes
        discount = self.rule_model._get_discount_for_customer_type('mayorista')
        self.assertEqual(discount, 10.0)

        # Verificar tipo 'none'
        discount_none = self.rule_model._get_discount_for_customer_type('none')
        self.assertEqual(discount_none, 0.0)

    def test_get_discount_inactive_rule(self):
        """Verificar que reglas inactivas no devuelven descuento"""
        # Desactivar regla VIP
        self.rule_vip.active = False
        
        # Crear regla inactiva explícitamente (redundante pero para probar creación inactiva)
        # self.rule_vip ya es inactiva, probamos con ella


        # No debería devolver descuento
        discount = self.rule_model._get_discount_for_customer_type('vip')
        self.assertEqual(discount, 0.0)

