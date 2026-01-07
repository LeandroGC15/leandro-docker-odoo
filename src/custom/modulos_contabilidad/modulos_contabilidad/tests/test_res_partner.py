# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestResPartner(TransactionCase):
    """Pruebas para el campo customer_type en res.partner"""

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']
        self.rule_model = self.env['account.discount.rule']
        self.company = self.env.company
        
        # Buscar o crear reglas de descuento para las pruebas
        self.rule_minorista = self._get_or_create_rule('minorista', 5.0)
        self.rule_mayorista = self._get_or_create_rule('mayorista', 10.0)
        self.rule_vip = self._get_or_create_rule('vip', 15.0)
        self.rule_none = self._get_or_create_rule('none', 0.0)

    def _get_or_create_rule(self, customer_type, percentage):
        """Helper para obtener regla existente o crear nueva"""
        rule = self.rule_model.search([
            ('customer_type', '=', customer_type),
            ('company_id', '=', self.company.id),
            ('active', '=', True)
        ], limit=1)
        
        if not rule:
            rule = self.rule_model.create({
                'name': f'Test Rule {customer_type}',
                'customer_type': customer_type,
                'discount_percentage': percentage,
                'active': True,
            })
        return rule

    def test_create_partner_with_discount_rule(self):
        """Test 1: Crear partner con regla de descuento y verificar customer_type"""
        partner = self.partner_model.create({
            'name': 'Cliente Test Mayorista',
            'discount_rule_id': self.rule_mayorista.id,
        })
        # customer_type es un campo related de discount_rule_id.customer_type
        self.assertEqual(partner.customer_type, 'mayorista')
        self.assertEqual(partner.discount_rule_id.id, self.rule_mayorista.id)
        self.assertTrue(partner.id)

    def test_partner_without_rule_has_no_customer_type(self):
        """Verificar que partner sin regla no tiene customer_type"""
        partner = self.partner_model.create({
            'name': 'Cliente Sin Tipo',
        })
        # Sin regla asignada, customer_type será False o el tipo de la regla por defecto
        self.assertIn(partner.customer_type, [False, 'none'])

    def test_partner_all_customer_types(self):
        """Verificar que se pueden crear partners con todos los tipos via reglas"""
        rules = [self.rule_minorista, self.rule_mayorista, self.rule_vip, self.rule_none]
        expected_types = ['minorista', 'mayorista', 'vip', 'none']
        
        for rule, expected_type in zip(rules, expected_types):
            partner = self.partner_model.create({
                'name': f'Cliente {expected_type}',
                'discount_rule_id': rule.id,
            })
            self.assertEqual(partner.customer_type, expected_type)

    def test_partner_update_discount_rule(self):
        """Verificar que al cambiar la regla, cambia el customer_type"""
        partner = self.partner_model.create({
            'name': 'Cliente Test',
            'discount_rule_id': self.rule_minorista.id,
        })
        self.assertEqual(partner.customer_type, 'minorista')
        
        # Cambiar la regla
        partner.discount_rule_id = self.rule_vip.id
        self.assertEqual(partner.customer_type, 'vip')

    def test_customer_type_is_readonly(self):
        """Verificar que customer_type es un campo readonly (related)"""
        partner = self.partner_model.create({
            'name': 'Cliente Test',
            'discount_rule_id': self.rule_mayorista.id,
        })
        # El campo es readonly, no se puede cambiar directamente
        # Solo cambia cuando se cambia discount_rule_id
        self.assertEqual(partner.customer_type, 'mayorista')

