# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestStockCriticalAlert(TransactionCase):
    """Pruebas para el módulo de alertas de stock crítico"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alert_model = cls.env['stock.critical.alert']
        cls.product_model = cls.env['product.template']
        cls.category_model = cls.env['product.category']
        
        # Crear categoría de prueba
        cls.category_electronics = cls.category_model.create({
            'name': 'Electrónicos Prueba',
        })
        cls.category_office = cls.category_model.create({
            'name': 'Oficina Prueba',
        })
        
        # Crear productos de prueba
        cls.product_laptop = cls.product_model.create({
            'name': 'Laptop de Prueba',
            'type': 'product',
            'categ_id': cls.category_electronics.id,
            'stock_minimum': 10.0,
        })
        cls.product_mouse = cls.product_model.create({
            'name': 'Mouse de Prueba',
            'type': 'product',
            'categ_id': cls.category_electronics.id,
            'stock_minimum': 20.0,
        })
        cls.product_paper = cls.product_model.create({
            'name': 'Papel de Prueba',
            'type': 'product',
            'categ_id': cls.category_office.id,
            'stock_minimum': 100.0,
        })
        cls.product_no_minimum = cls.product_model.create({
            'name': 'Producto Sin Mínimo',
            'type': 'product',
            'categ_id': cls.category_office.id,
            'stock_minimum': 0.0,
        })

    def test_01_product_stock_minimum_field(self):
        """Test: Verificar que el campo stock_minimum existe y funciona"""
        self.assertEqual(self.product_laptop.stock_minimum, 10.0)
        self.assertEqual(self.product_mouse.stock_minimum, 20.0)
        self.assertEqual(self.product_no_minimum.stock_minimum, 0.0)

    def test_02_is_stock_critical_computation(self):
        """Test: Verificar cálculo de is_stock_critical"""
        # Por defecto qty_available es 0, menor que stock_minimum = 10
        self.assertTrue(self.product_laptop.is_stock_critical)
        self.assertTrue(self.product_mouse.is_stock_critical)
        
        # Producto sin mínimo no debe ser crítico
        self.assertFalse(self.product_no_minimum.is_stock_critical)

    def test_03_create_alert(self):
        """Test: Crear alerta de stock crítico"""
        alert = self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 5.0,
        })
        
        self.assertTrue(alert.id)
        self.assertEqual(alert.state, 'open')
        self.assertEqual(alert.product_tmpl_id, self.product_laptop)
        self.assertEqual(alert.category_id, self.category_electronics)
        self.assertEqual(alert.qty_available_at_alert, 5.0)

    def test_04_no_duplicate_alerts(self):
        """Test: No se generan alertas duplicadas para el mismo producto"""
        # Crear primera alerta
        alert1 = self.alert_model.create_alert_if_not_exists(self.product_laptop)
        
        # Intentar crear otra alerta para el mismo producto
        alert2 = self.alert_model.create_alert_if_not_exists(self.product_laptop)
        
        # Deben ser la misma alerta
        self.assertEqual(alert1.id, alert2.id)
        
        # Verificar que solo hay una alerta abierta
        alerts_count = self.alert_model.search_count([
            ('product_tmpl_id', '=', self.product_laptop.id),
            ('state', '=', 'open'),
        ])
        self.assertEqual(alerts_count, 1)

    def test_05_allow_new_alert_after_resolution(self):
        """Test: Se puede crear nueva alerta después de resolver la anterior"""
        # Crear primera alerta
        alert1 = self.alert_model.create_alert_if_not_exists(self.product_mouse)
        
        # Resolver la alerta
        alert1.action_resolve()
        self.assertEqual(alert1.state, 'resolved')
        
        # Crear nueva alerta
        alert2 = self.alert_model.create_alert_if_not_exists(self.product_mouse)
        
        # Debe ser una alerta diferente
        self.assertNotEqual(alert1.id, alert2.id)
        self.assertEqual(alert2.state, 'open')

    def test_06_alert_states_transitions(self):
        """Test: Transiciones de estado de alertas"""
        alert = self.alert_model.create({
            'product_tmpl_id': self.product_paper.id,
            'qty_available_at_alert': 50.0,
        })
        
        # Estado inicial
        self.assertEqual(alert.state, 'open')
        self.assertFalse(alert.resolution_date)
        
        # Resolver
        alert.action_resolve()
        self.assertEqual(alert.state, 'resolved')
        self.assertTrue(alert.resolution_date)
        
        # Reabrir
        alert.action_reopen()
        self.assertEqual(alert.state, 'open')
        self.assertFalse(alert.resolution_date)
        
        # Cancelar
        alert.action_cancel()
        self.assertEqual(alert.state, 'cancelled')

    def test_07_deficit_computation(self):
        """Test: Verificar cálculo del déficit"""
        alert = self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 3.0,
        })
        
        # Déficit = stock_minimum (10) - qty_available (0 por defecto)
        self.assertEqual(alert.deficit, 10.0)

    def test_08_cron_creates_alerts(self):
        """Test: El cron genera alertas para productos críticos"""
        # Ejecutar el cron
        self.alert_model._cron_check_stock_alerts()
        
        # Verificar que se crearon alertas para productos con stock bajo
        laptop_alerts = self.alert_model.search([
            ('product_tmpl_id', '=', self.product_laptop.id),
            ('state', '=', 'open'),
        ])
        self.assertTrue(len(laptop_alerts) > 0)
        
        # No debe haber alerta para producto sin mínimo
        no_min_alerts = self.alert_model.search([
            ('product_tmpl_id', '=', self.product_no_minimum.id),
        ])
        self.assertEqual(len(no_min_alerts), 0)

    def test_09_cron_no_duplicate_on_rerun(self):
        """Test: El cron no crea duplicados al ejecutarse múltiples veces"""
        # Ejecutar cron primera vez
        self.alert_model._cron_check_stock_alerts()
        
        # Contar alertas
        count1 = self.alert_model.search_count([
            ('product_tmpl_id', '=', self.product_laptop.id),
            ('state', '=', 'open'),
        ])
        
        # Ejecutar cron segunda vez
        self.alert_model._cron_check_stock_alerts()
        
        # Contar alertas nuevamente
        count2 = self.alert_model.search_count([
            ('product_tmpl_id', '=', self.product_laptop.id),
            ('state', '=', 'open'),
        ])
        
        # Debe ser la misma cantidad (no duplicados)
        self.assertEqual(count1, count2)
        self.assertEqual(count1, 1)

    def test_10_alert_display_name(self):
        """Test: Verificar generación del display_name"""
        alert = self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 5.0,
        })
        
        self.assertIn('Laptop de Prueba', alert.display_name)
        self.assertIn('Alerta:', alert.display_name)

    def test_11_category_grouping(self):
        """Test: Verificar que las alertas se pueden agrupar por categoría"""
        # Crear alertas para diferentes productos
        alert1 = self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 5.0,
        })
        alert2 = self.alert_model.create({
            'product_tmpl_id': self.product_paper.id,
            'qty_available_at_alert': 50.0,
        })
        
        # Verificar categorías
        self.assertEqual(alert1.category_id.name, 'Electrónicos Prueba')
        self.assertEqual(alert2.category_id.name, 'Oficina Prueba')
        
        # Buscar alertas por categoría
        electronics_alerts = self.alert_model.search([
            ('category_id', '=', self.category_electronics.id),
        ])
        self.assertIn(alert1, electronics_alerts)
        self.assertNotIn(alert2, electronics_alerts)

    def test_12_mail_message_creation(self):
        """Test: Verificar que se crea mensaje en mail.message"""
        # Crear alerta usando el método que genera notificación
        alert = self.alert_model.create_alert_if_not_exists(self.product_laptop)
        
        # Verificar que se creó al menos un mensaje
        messages = alert.message_ids.filtered(
            lambda m: 'Stock Crítico' in (m.body or '')
        )
        self.assertTrue(len(messages) > 0, "Debe existir un mensaje de notificación")

    def test_13_product_alert_count(self):
        """Test: Verificar contador de alertas en producto"""
        # Inicialmente sin alertas
        self.product_laptop.invalidate_recordset()
        initial_count = self.product_laptop.stock_alert_count
        
        # Crear alerta
        self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 5.0,
        })
        
        # Refrescar y verificar contador
        self.product_laptop.invalidate_recordset()
        new_count = self.product_laptop.stock_alert_count
        
        self.assertEqual(new_count, initial_count + 1)

    def test_14_search_critical_products(self):
        """Test: Buscar productos con stock crítico"""
        critical_products = self.product_model.search([
            ('is_stock_critical', '=', True),
        ])
        
        # Productos con stock_minimum > 0 y qty_available < stock_minimum
        self.assertIn(self.product_laptop, critical_products)
        self.assertIn(self.product_mouse, critical_products)
        self.assertNotIn(self.product_no_minimum, critical_products)

    def test_15_inactive_alert_allows_new(self):
        """Test: Una alerta inactiva permite crear nueva"""
        # Crear primera alerta
        alert1 = self.alert_model.create({
            'product_tmpl_id': self.product_laptop.id,
            'qty_available_at_alert': 5.0,
        })
        
        # Desactivar la alerta
        alert1.active = False
        
        # Crear nueva alerta
        alert2 = self.alert_model.create_alert_if_not_exists(self.product_laptop)
        
        # Debe ser una nueva alerta
        self.assertNotEqual(alert1.id, alert2.id)
        self.assertTrue(alert2.active)

