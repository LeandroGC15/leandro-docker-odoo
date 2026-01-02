# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo import fields


class TestAccountMoveDiscount(TransactionCase):
    """Pruebas para la aplicación automática de descuentos en facturas"""

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.move_model = self.env['account.move']
        self.rule_model = self.env['account.discount.rule']

        # Crear productos de prueba
        self.product = self.product_model.create({
            'name': 'Producto Test',
            'type': 'consu',
            'list_price': 100.0,
        })

        # Crear reglas de descuento
        self.rule_minorista = self.rule_model.create({
            'name': 'Descuento Minorista 5%',
            'customer_type': 'minorista',
            'discount_percentage': 5.0,
            'active': True,
        })
        self.rule_mayorista = self.rule_model.create({
            'name': 'Descuento Mayorista 10%',
            'customer_type': 'mayorista',
            'discount_percentage': 10.0,
            'active': True,
        })
        self.rule_vip = self.rule_model.create({
            'name': 'Descuento VIP 15%',
            'customer_type': 'vip',
            'discount_percentage': 15.0,
            'active': True,
        })
        self.rule_none = self.rule_model.create({
            'name': 'Sin tipo',
            'customer_type': 'none',
            'discount_percentage': 0.0,
            'active': True,
        })

    def test_invoice_auto_discount_mayorista(self):
        """Test 3: Aplicación automática de descuento para mayorista"""
        # Crear partner mayorista (con regla asignada)
        partner = self.partner_model.create({
            'name': 'Cliente Mayorista',
            'discount_rule_id': self.rule_mayorista.id,
        })
        # Verificar que customer_type se calcula correctamente
        self.assertEqual(partner.customer_type, 'mayorista')

        # Crear factura
        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        # Aplicar descuentos automáticos
        invoice._apply_automatic_discounts()

        # Verificar que se aplicó el descuento del 10%
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 10.0)

    def test_invoice_auto_discount_vip(self):
        """Aplicación automática de descuento para VIP"""
        partner = self.partner_model.create({
            'name': 'Cliente VIP',
            'discount_rule_id': self.rule_vip.id,
        })
        self.assertEqual(partner.customer_type, 'vip')

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        invoice._apply_automatic_discounts()

        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 15.0)

    def test_invoice_no_discount_no_customer_type(self):
        """Test 4: Cliente sin tipo definido no debe aplicar descuento"""
        partner = self.partner_model.create({
            'name': 'Cliente Sin Tipo',
            'discount_rule_id': self.rule_none.id,
        })
        self.assertEqual(partner.customer_type, 'none')

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        invoice._apply_automatic_discounts()

        # No debería aplicarse descuento
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 0.0)

    def test_invoice_no_discount_partner_without_rule(self):
        """Cliente sin regla asignada no debe aplicar descuento"""
        partner = self.partner_model.create({
            'name': 'Cliente Sin Regla',
            # No asignamos discount_rule_id
        })

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        invoice._apply_automatic_discounts()

        # No debería aplicarse descuento
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 0.0)

    def test_invoice_no_discount_vendor_bill(self):
        """Test 5: Factura de proveedor no debe aplicar descuento"""
        partner = self.partner_model.create({
            'name': 'Proveedor',
            'discount_rule_id': self.rule_mayorista.id,  # Aunque tenga tipo, es proveedor
        })

        invoice = self.move_model.create({
            'move_type': 'in_invoice',  # Factura de proveedor
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        invoice._apply_automatic_discounts()

        # No debería aplicarse descuento en facturas de proveedor
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 0.0)

    def test_invoice_multiple_lines_discount(self):
        """Test 5: Factura con múltiples líneas"""
        partner = self.partner_model.create({
            'name': 'Cliente Mayorista',
            'discount_rule_id': self.rule_mayorista.id,
        })

        product2 = self.product_model.create({
            'name': 'Producto 2',
            'type': 'consu',
            'list_price': 200.0,
        })

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1,
                    'price_unit': 100.0,
                }),
                (0, 0, {
                    'product_id': product2.id,
                    'quantity': 2,
                    'price_unit': 200.0,
                }),
            ],
        })

        invoice._apply_automatic_discounts()

        # Todas las líneas deberían tener el descuento
        for line in invoice.invoice_line_ids:
            if line.product_id:  # Solo líneas de producto
                self.assertEqual(line.discount, 10.0)

    def test_invoice_existing_discount_not_overwritten(self):
        """Test 5: Factura con descuento manual existente"""
        partner = self.partner_model.create({
            'name': 'Cliente Mayorista',
            'discount_rule_id': self.rule_mayorista.id,
        })

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
                'discount': 20.0,  # Descuento manual previo
            })],
        })

        invoice._apply_automatic_discounts()

        # El descuento manual debería mantenerse (lógica actual no sobrescribe)
        # Nota: La implementación actual solo aplica si discount == 0
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 20.0)

    def test_invoice_line_create_auto_applies_discount(self):
        """Verificar que al crear línea de factura se aplica descuento automático"""
        partner = self.partner_model.create({
            'name': 'Cliente Minorista',
            'discount_rule_id': self.rule_minorista.id,
        })

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
        })

        # Crear línea (debería aplicar descuento automáticamente)
        line = self.env['account.move.line'].create({
            'move_id': invoice.id,
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': 100.0,
        })

        # Verificar que se aplicó el descuento
        self.assertEqual(line.discount, 5.0)

    def test_invoice_refund_auto_discount(self):
        """Verificar que notas de crédito también aplican descuento"""
        partner = self.partner_model.create({
            'name': 'Cliente Mayorista',
            'discount_rule_id': self.rule_mayorista.id,
        })

        invoice = self.move_model.create({
            'move_type': 'out_refund',  # Nota de crédito
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        invoice._apply_automatic_discounts()

        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 10.0)

    def test_invoice_validate_applies_discount(self):
        """Verificar que al validar la factura se aplican los descuentos"""
        partner = self.partner_model.create({
            'name': 'Cliente VIP',
            'discount_rule_id': self.rule_vip.id,
        })

        invoice = self.move_model.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })

        # Antes de validar, limpiamos el descuento para simular que no se aplicó antes
        invoice.invoice_line_ids[0].discount = 0.0

        # Al validar, debería aplicar el descuento
        invoice.action_post()

        # Verificar que se aplicó el descuento del 15%
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.discount, 15.0)

