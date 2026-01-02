# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestProductCrossSell(TransactionCase):
    """Pruebas para el modelo product.cross.sell"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cross_sell_model = cls.env['product.cross.sell']
        cls.product_model = cls.env['product.template']
        
        # Crear productos de prueba
        cls.product_laptop = cls.product_model.create({
            'name': 'Laptop de Prueba',
            'list_price': 1000.0,
            'type': 'consu',
        })
        cls.product_mouse = cls.product_model.create({
            'name': 'Mouse de Prueba',
            'list_price': 50.0,
            'type': 'consu',
        })
        cls.product_keyboard = cls.product_model.create({
            'name': 'Teclado de Prueba',
            'list_price': 80.0,
            'type': 'consu',
        })
        cls.product_monitor = cls.product_model.create({
            'name': 'Monitor de Prueba',
            'list_price': 300.0,
            'type': 'consu',
        })

    def test_01_create_cross_sell_rule(self):
        """Test: Crear regla de cross-selling válida"""
        rule = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        
        self.assertTrue(rule.id)
        self.assertTrue(rule.active)
        self.assertEqual(rule.source_product_tmpl_id, self.product_laptop)
        self.assertEqual(rule.suggested_product_tmpl_id, self.product_mouse)

    def test_02_auto_compute_name(self):
        """Test: Verificar que el nombre se calcula automáticamente"""
        rule = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        
        expected_name = f"{self.product_laptop.name} → {self.product_mouse.name}"
        self.assertEqual(rule.name, expected_name)

    def test_03_same_product_validation(self):
        """Test: No se puede crear regla con el mismo producto como origen y sugerido"""
        with self.assertRaises(ValidationError):
            self.cross_sell_model.create({
                'source_product_tmpl_id': self.product_laptop.id,
                'suggested_product_tmpl_id': self.product_laptop.id,
            })

    def test_04_unique_relation_validation(self):
        """Test: No se puede crear regla duplicada activa"""
        # Crear primera regla
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        
        # Intentar crear regla duplicada
        with self.assertRaises(ValidationError):
            self.cross_sell_model.create({
                'source_product_tmpl_id': self.product_laptop.id,
                'suggested_product_tmpl_id': self.product_mouse.id,
            })

    def test_05_allow_inactive_duplicate(self):
        """Test: Se puede crear regla duplicada si está inactiva"""
        # Crear primera regla
        rule1 = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_keyboard.id,
        })
        
        # Desactivar la primera regla
        rule1.active = False
        
        # Crear regla "duplicada" (pero la primera está inactiva)
        rule2 = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_keyboard.id,
        })
        
        self.assertTrue(rule2.id)
        self.assertTrue(rule2.active)

    def test_06_get_cross_sell_products_simple(self):
        """Test: Obtener productos sugeridos para un producto"""
        # Crear reglas
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_monitor.id,
        })
        
        # Obtener sugerencias
        suggestions = self.cross_sell_model.get_cross_sell_products(
            [self.product_laptop.id]
        )
        
        self.assertEqual(len(suggestions), 2)
        self.assertIn(self.product_mouse, suggestions)
        self.assertIn(self.product_monitor, suggestions)

    def test_07_get_cross_sell_products_bidirectional(self):
        """Test: Obtener productos sugeridos con relación bidireccional"""
        # Crear regla bidireccional
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
            'bidirectional': True,
        })
        
        # Sugerencias desde laptop -> mouse
        suggestions_from_laptop = self.cross_sell_model.get_cross_sell_products(
            [self.product_laptop.id]
        )
        self.assertIn(self.product_mouse, suggestions_from_laptop)
        
        # Sugerencias desde mouse -> laptop (bidireccional)
        suggestions_from_mouse = self.cross_sell_model.get_cross_sell_products(
            [self.product_mouse.id]
        )
        self.assertIn(self.product_laptop, suggestions_from_mouse)

    def test_08_get_cross_sell_excludes_source_products(self):
        """Test: Las sugerencias no incluyen productos que ya están en la lista"""
        # Crear regla
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        
        # Buscar sugerencias incluyendo el mouse como producto existente
        suggestions = self.cross_sell_model.get_cross_sell_products(
            [self.product_laptop.id, self.product_mouse.id]
        )
        
        # El mouse no debe aparecer en sugerencias porque ya está
        self.assertNotIn(self.product_mouse, suggestions)

    def test_09_inactive_rules_not_returned(self):
        """Test: Las reglas inactivas no devuelven sugerencias"""
        # Crear regla inactiva
        rule = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
            'active': False,
        })
        
        suggestions = self.cross_sell_model.get_cross_sell_products(
            [self.product_laptop.id]
        )
        
        self.assertNotIn(self.product_mouse, suggestions)

    def test_10_copy_rule_inactive(self):
        """Test: Al duplicar una regla, se crea inactiva"""
        rule = self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        
        self.assertTrue(rule.active)
        
        copied_rule = rule.copy()
        
        self.assertFalse(copied_rule.active)

    def test_11_product_template_cross_sell_count(self):
        """Test: Contador de cross-sells en producto"""
        # Inicialmente sin reglas
        self.assertEqual(self.product_laptop.cross_sell_count, 0)
        
        # Crear reglas
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_monitor.id,
        })
        
        # Refrescar el registro
        self.product_laptop.invalidate_recordset()
        
        self.assertEqual(self.product_laptop.cross_sell_count, 2)

    def test_12_multiple_products_suggestions(self):
        """Test: Obtener sugerencias para múltiples productos"""
        # Crear reglas para diferentes productos
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_laptop.id,
            'suggested_product_tmpl_id': self.product_mouse.id,
        })
        self.cross_sell_model.create({
            'source_product_tmpl_id': self.product_monitor.id,
            'suggested_product_tmpl_id': self.product_keyboard.id,
        })
        
        # Buscar sugerencias para laptop y monitor
        suggestions = self.cross_sell_model.get_cross_sell_products(
            [self.product_laptop.id, self.product_monitor.id]
        )
        
        self.assertEqual(len(suggestions), 2)
        self.assertIn(self.product_mouse, suggestions)
        self.assertIn(self.product_keyboard, suggestions)

