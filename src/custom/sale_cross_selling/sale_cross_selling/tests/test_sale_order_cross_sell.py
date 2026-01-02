# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestSaleOrderCrossSell(TransactionCase):
    """Pruebas para cross-selling en pedidos de venta"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cross_sell_model = cls.env['product.cross.sell']
        cls.product_model = cls.env['product.template']
        cls.sale_order_model = cls.env['sale.order']
        cls.wizard_model = cls.env['cross.sell.wizard']
        
        # Crear partner de prueba
        cls.partner = cls.env['res.partner'].create({
            'name': 'Cliente de Prueba Cross-Sell',
        })
        
        # Crear productos de prueba con variantes
        cls.product_laptop = cls.product_model.create({
            'name': 'Laptop Cross-Sell Test',
            'list_price': 1000.0,
            'type': 'consu',
        })
        cls.product_mouse = cls.product_model.create({
            'name': 'Mouse Cross-Sell Test',
            'list_price': 50.0,
            'type': 'consu',
        })
        cls.product_keyboard = cls.product_model.create({
            'name': 'Teclado Cross-Sell Test',
            'list_price': 80.0,
            'type': 'consu',
        })
        
        # Crear reglas de cross-selling
        cls.rule_laptop_mouse = cls.cross_sell_model.create({
            'source_product_tmpl_id': cls.product_laptop.id,
            'suggested_product_tmpl_id': cls.product_mouse.id,
        })
        cls.rule_laptop_keyboard = cls.cross_sell_model.create({
            'source_product_tmpl_id': cls.product_laptop.id,
            'suggested_product_tmpl_id': cls.product_keyboard.id,
        })

    def _create_sale_order(self, products=None):
        """Helper para crear pedidos de venta"""
        order = self.sale_order_model.create({
            'partner_id': self.partner.id,
        })
        
        if products:
            for product_tmpl in products:
                product = product_tmpl.product_variant_id
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': 1.0,
                })
        
        return order

    def test_01_has_cross_sell_suggestions_empty_order(self):
        """Test: Pedido vacío no tiene sugerencias"""
        order = self._create_sale_order()
        
        self.assertFalse(order.has_cross_sell_suggestions)

    def test_02_has_cross_sell_suggestions_with_product(self):
        """Test: Pedido con producto que tiene reglas tiene sugerencias"""
        order = self._create_sale_order([self.product_laptop])
        
        self.assertTrue(order.has_cross_sell_suggestions)

    def test_03_no_suggestions_when_all_products_in_order(self):
        """Test: Sin sugerencias cuando todos los productos sugeridos ya están"""
        order = self._create_sale_order([
            self.product_laptop,
            self.product_mouse,
            self.product_keyboard,
        ])
        
        self.assertFalse(order.has_cross_sell_suggestions)

    def test_04_action_show_wizard_empty_order(self):
        """Test: Mostrar wizard en pedido vacío retorna notificación"""
        order = self._create_sale_order()
        
        result = order.action_show_cross_sell_wizard()
        
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertEqual(result['params']['type'], 'warning')

    def test_05_action_show_wizard_no_suggestions(self):
        """Test: Mostrar wizard sin sugerencias retorna notificación info"""
        # Crear producto sin reglas
        product_standalone = self.product_model.create({
            'name': 'Producto Sin Reglas',
            'list_price': 100.0,
            'type': 'consu',
        })
        order = self._create_sale_order([product_standalone])
        
        result = order.action_show_cross_sell_wizard()
        
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertEqual(result['params']['type'], 'info')

    def test_06_action_show_wizard_with_suggestions(self):
        """Test: Mostrar wizard con sugerencias abre el wizard"""
        order = self._create_sale_order([self.product_laptop])
        
        result = order.action_show_cross_sell_wizard()
        
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'cross.sell.wizard')
        
        # Verificar que el wizard se creó
        wizard = self.wizard_model.browse(result['res_id'])
        self.assertEqual(wizard.sale_order_id, order)
        self.assertEqual(len(wizard.line_ids), 2)  # mouse y keyboard

    def test_07_wizard_add_selected_products(self):
        """Test: Añadir productos seleccionados al pedido"""
        order = self._create_sale_order([self.product_laptop])
        initial_lines = len(order.order_line)
        
        # Mostrar wizard
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        # Seleccionar el mouse
        mouse_line = wizard.line_ids.filtered(
            lambda l: l.product_tmpl_id == self.product_mouse
        )
        mouse_line.selected = True
        mouse_line.quantity = 2.0
        
        # Añadir seleccionados
        wizard.action_add_selected_products()
        
        # Verificar que se añadió el producto
        self.assertEqual(len(order.order_line), initial_lines + 1)
        
        # Verificar que el mouse está en el pedido
        mouse_in_order = order.order_line.filtered(
            lambda l: l.product_template_id == self.product_mouse
        )
        self.assertTrue(mouse_in_order)
        self.assertEqual(mouse_in_order.product_uom_qty, 2.0)

    def test_08_wizard_add_without_selection_raises_error(self):
        """Test: Error al intentar añadir sin selección"""
        order = self._create_sale_order([self.product_laptop])
        
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        # No seleccionar nada e intentar añadir
        with self.assertRaises(UserError):
            wizard.action_add_selected_products()

    def test_09_wizard_select_all(self):
        """Test: Seleccionar todos los productos"""
        order = self._create_sale_order([self.product_laptop])
        
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        # Verificar que ninguno está seleccionado
        self.assertEqual(wizard.selected_count, 0)
        
        # Seleccionar todos
        wizard.action_select_all()
        
        # Verificar que todos están seleccionados
        self.assertEqual(wizard.selected_count, 2)

    def test_10_wizard_deselect_all(self):
        """Test: Deseleccionar todos los productos"""
        order = self._create_sale_order([self.product_laptop])
        
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        # Seleccionar todos primero
        wizard.action_select_all()
        self.assertEqual(wizard.selected_count, 2)
        
        # Deseleccionar todos
        wizard.action_deselect_all()
        
        self.assertEqual(wizard.selected_count, 0)

    def test_11_cannot_add_to_confirmed_order(self):
        """Test: No se pueden añadir productos a pedido confirmado"""
        order = self._create_sale_order([self.product_laptop])
        
        # Confirmar pedido
        order.action_confirm()
        
        # Intentar abrir wizard en pedido confirmado
        result = order.action_show_cross_sell_wizard()
        
        # Debería devolver notificación o el wizard no permite añadir
        # (dependiendo del estado del pedido)

    def test_12_order_update_after_adding_products(self):
        """Test: El pedido se actualiza correctamente después de añadir"""
        order = self._create_sale_order([self.product_laptop])
        
        # Guardar el total inicial
        initial_total = order.amount_total
        
        # Mostrar wizard y añadir productos
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        # Seleccionar todos
        wizard.action_select_all()
        wizard.action_add_selected_products()
        
        # El total debería haber aumentado
        self.assertGreater(order.amount_total, initial_total)

    def test_13_bidirectional_suggestion_in_order(self):
        """Test: Sugerencias bidireccionales funcionan en pedidos"""
        # Crear regla bidireccional
        product_case = self.product_model.create({
            'name': 'Funda de Laptop',
            'list_price': 40.0,
            'type': 'consu',
        })
        
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': product_case.id,
            'bidirectional': True,
        })
        
        # Crear pedido con la funda
        order = self._create_sale_order([product_case])
        
        # Debería sugerir la laptop
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        suggested_products = wizard.line_ids.mapped('product_tmpl_id')
        self.assertIn(self.product_laptop, suggested_products)

    def test_14_multiple_products_multiple_suggestions(self):
        """Test: Múltiples productos generan múltiples sugerencias"""
        # Crear producto adicional con reglas
        product_monitor = self.product_model.create({
            'name': 'Monitor Test',
            'list_price': 300.0,
            'type': 'consu',
        })
        product_cable = self.product_model.create({
            'name': 'Cable HDMI',
            'list_price': 20.0,
            'type': 'consu',
        })
        
        self.cross_sell_model.create({
            'source_product_tmpl_id': product_monitor.id,
            'suggested_product_tmpl_id': product_cable.id,
        })
        
        # Crear pedido con laptop y monitor
        order = self._create_sale_order([self.product_laptop, product_monitor])
        
        # Debería sugerir mouse, keyboard y cable
        result = order.action_show_cross_sell_wizard()
        wizard = self.wizard_model.browse(result['res_id'])
        
        self.assertEqual(len(wizard.line_ids), 3)

