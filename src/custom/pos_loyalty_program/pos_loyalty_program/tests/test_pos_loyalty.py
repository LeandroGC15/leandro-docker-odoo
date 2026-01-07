# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPosLoyaltyProgram(TransactionCase):
    """Pruebas para el programa de fidelización POS"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env['res.partner']
        cls.pos_config_model = cls.env['pos.config']
        cls.pos_order_model = cls.env['pos.order']
        cls.pos_session_model = cls.env['pos.session']
        cls.loyalty_history_model = cls.env['pos.loyalty.history']
        
        # Crear partner de prueba
        cls.partner = cls.partner_model.create({
            'name': 'Cliente Fidelización Test',
            'email': 'fidelizacion@test.com',
        })
        
        # Crear producto de prueba
        cls.product = cls.env['product.product'].create({
            'name': 'Producto Fidelización Test',
            'list_price': 100.0,
            'type': 'consu',
            'available_in_pos': True,
        })
        
        # Crear método de pago exclusivo para POS con fidelización
        # En Odoo 17, métodos de pago en efectivo no pueden compartirse entre POS
        cls.payment_method = cls.env['pos.payment.method'].create({
            'name': 'Efectivo Fidelización Test',
            'is_cash_count': True,
        })
        
        # Crear método de pago exclusivo para POS sin fidelización
        cls.payment_method_no_loyalty = cls.env['pos.payment.method'].create({
            'name': 'Efectivo Sin Fidelización Test',
            'is_cash_count': True,
        })
        
        # Crear configuración de POS con fidelización habilitada
        cls.pos_config = cls.pos_config_model.create({
            'name': 'POS Fidelización Test',
            'loyalty_program_enabled': True,
            'loyalty_points_per_amount': 1.0,
            'loyalty_amount_per_points': 10.0,
            'loyalty_points_rounding': 'floor',
            'payment_method_ids': [(4, cls.payment_method.id)],
        })
        
        # Crear configuración sin fidelización
        cls.pos_config_no_loyalty = cls.pos_config_model.create({
            'name': 'POS Sin Fidelización Test',
            'loyalty_program_enabled': False,
            'payment_method_ids': [(4, cls.payment_method_no_loyalty.id)],
        })

    def _create_pos_session(self, config):
        """Helper para crear sesión de POS"""
        session = self.pos_session_model.create({
            'config_id': config.id,
            'user_id': self.env.user.id,
        })
        return session

    def _create_pos_order(self, session, partner, amount):
        """Helper para crear orden de POS"""
        order = self.pos_order_model.create({
            'session_id': session.id,
            'config_id': session.config_id.id,
            'partner_id': partner.id if partner else False,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': amount,
                'qty': 1.0,
                'price_subtotal': amount,
                'price_subtotal_incl': amount,
            })],
            'amount_total': amount,
            'amount_tax': 0.0,
            'amount_paid': amount,
            'amount_return': 0.0,
        })
        return order

    def test_01_partner_loyalty_points_field(self):
        """Test: Verificar campo de puntos de fidelización en partner"""
        self.assertEqual(self.partner.loyalty_points, 0.0)
        self.assertEqual(self.partner.loyalty_history_count, 0)
        self.assertEqual(self.partner.loyalty_points_total_earned, 0.0)
        self.assertEqual(self.partner.loyalty_points_total_redeemed, 0.0)

    def test_02_pos_config_loyalty_settings(self):
        """Test: Verificar configuración de fidelización en pos.config"""
        self.assertTrue(self.pos_config.loyalty_program_enabled)
        self.assertEqual(self.pos_config.loyalty_points_per_amount, 1.0)
        self.assertEqual(self.pos_config.loyalty_amount_per_points, 10.0)
        self.assertEqual(self.pos_config.loyalty_points_rounding, 'floor')

    def test_03_points_calculation_basic(self):
        """Test: Calcular puntos con configuración básica (1 punto por cada $10)"""
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 100.0)
        
        # Calcular puntos: $100 / $10 * 1 = 10 puntos
        points = order._calculate_loyalty_points()
        self.assertEqual(points, 10.0)

    def test_04_points_calculation_custom_config(self):
        """Test: Calcular puntos con configuración personalizada"""
        # Configurar: 2 puntos por cada $5
        self.pos_config.write({
            'loyalty_points_per_amount': 2.0,
            'loyalty_amount_per_points': 5.0,
        })
        
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 100.0)
        
        # Calcular puntos: $100 / $5 * 2 = 40 puntos
        points = order._calculate_loyalty_points()
        self.assertEqual(points, 40.0)
        
        # Restaurar configuración
        self.pos_config.write({
            'loyalty_points_per_amount': 1.0,
            'loyalty_amount_per_points': 10.0,
        })

    def test_05_points_accumulation_on_order_paid(self):
        """Test: Acumular puntos al validar orden de POS"""
        initial_points = self.partner.loyalty_points
        
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 100.0)
        
        # Simular pago - crear payment y llamar action_pos_order_paid
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'amount': 100.0,
            'payment_method_id': self.payment_method.id,
        })
        order.action_pos_order_paid()
        
        # Verificar puntos acumulados: $100 / $10 * 1 = 10 puntos
        self.assertEqual(order.loyalty_points_earned, 10.0)
        self.assertEqual(self.partner.loyalty_points, initial_points + 10.0)

    def test_06_loyalty_history_created(self):
        """Test: Verificar creación de histórico de puntos"""
        initial_history_count = len(self.partner.loyalty_history_ids)
        
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 50.0)
        
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'amount': 50.0,
            'payment_method_id': self.payment_method.id,
        })
        order.action_pos_order_paid()
        
        # Verificar que se creó registro de histórico
        self.assertEqual(len(self.partner.loyalty_history_ids), initial_history_count + 1)
        
        # Verificar datos del histórico
        last_history = self.partner.loyalty_history_ids.sorted('date', reverse=True)[0]
        self.assertEqual(last_history.order_id, order)
        self.assertEqual(last_history.transaction_type, 'earned')
        self.assertEqual(last_history.points, 5.0)  # $50 / $10 = 5 puntos
        self.assertEqual(last_history.order_amount, 50.0)

    def test_07_session_points_summary(self):
        """Test: Verificar resumen de puntos en sesión"""
        session = self._create_pos_session(self.pos_config)
        
        # Crear y pagar múltiples órdenes
        for amount in [100.0, 50.0, 75.0]:
            order = self._create_pos_order(session, self.partner, amount)
            self.env['pos.payment'].create({
                'pos_order_id': order.id,
                'amount': amount,
                'payment_method_id': self.payment_method.id,
            })
            order.action_pos_order_paid()
        
        # Calcular totales esperados: 10 + 5 + 7 = 22 puntos
        session._compute_loyalty_summary()
        self.assertEqual(session.loyalty_points_earned, 22.0)
        self.assertEqual(session.loyalty_transactions_count, 3)

    def test_08_points_rounding_floor(self):
        """Test: Redondeo hacia abajo"""
        self.pos_config.loyalty_points_rounding = 'floor'
        
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 99.0)  # $99 / $10 = 9.9 -> 9
        
        points = order._calculate_loyalty_points()
        self.assertEqual(points, 9.0)

    def test_09_points_rounding_ceiling(self):
        """Test: Redondeo hacia arriba"""
        self.pos_config.loyalty_points_rounding = 'ceiling'
        
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 91.0)  # $91 / $10 = 9.1 -> 10
        
        points = order._calculate_loyalty_points()
        self.assertEqual(points, 10.0)

    def test_10_points_rounding_nearest(self):
        """Test: Redondeo al más cercano"""
        self.pos_config.loyalty_points_rounding = 'nearest'
        
        session = self._create_pos_session(self.pos_config)
        
        # 9.4 -> 9
        order1 = self._create_pos_order(session, self.partner, 94.0)
        self.assertEqual(order1._calculate_loyalty_points(), 9.0)
        
        # 9.5 -> 10
        order2 = self._create_pos_order(session, self.partner, 95.0)
        self.assertEqual(order2._calculate_loyalty_points(), 10.0)
        
        # Restaurar
        self.pos_config.loyalty_points_rounding = 'floor'

    def test_11_loyalty_disabled(self):
        """Test: No acumular puntos cuando está deshabilitado"""
        initial_points = self.partner.loyalty_points
        
        session = self._create_pos_session(self.pos_config_no_loyalty)
        order = self._create_pos_order(session, self.partner, 100.0)
        
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'amount': 100.0,
            'payment_method_id': self.payment_method_no_loyalty.id,
        })
        order.action_pos_order_paid()
        
        # No debería haber puntos
        self.assertEqual(order.loyalty_points_earned, 0.0)
        self.assertEqual(self.partner.loyalty_points, initial_points)

    def test_12_multiple_orders_accumulation(self):
        """Test: Acumulación de puntos de múltiples órdenes"""
        # Resetear puntos del partner
        self.partner.loyalty_points = 0.0
        
        session = self._create_pos_session(self.pos_config)
        
        # Orden 1: $100 = 10 puntos
        order1 = self._create_pos_order(session, self.partner, 100.0)
        self.env['pos.payment'].create({
            'pos_order_id': order1.id,
            'amount': 100.0,
            'payment_method_id': self.payment_method.id,
        })
        order1.action_pos_order_paid()
        self.assertEqual(self.partner.loyalty_points, 10.0)
        
        # Orden 2: $50 = 5 puntos
        order2 = self._create_pos_order(session, self.partner, 50.0)
        self.env['pos.payment'].create({
            'pos_order_id': order2.id,
            'amount': 50.0,
            'payment_method_id': self.payment_method.id,
        })
        order2.action_pos_order_paid()
        self.assertEqual(self.partner.loyalty_points, 15.0)
        
        # Orden 3: $200 = 20 puntos
        order3 = self._create_pos_order(session, self.partner, 200.0)
        self.env['pos.payment'].create({
            'pos_order_id': order3.id,
            'amount': 200.0,
            'payment_method_id': self.payment_method.id,
        })
        order3.action_pos_order_paid()
        self.assertEqual(self.partner.loyalty_points, 35.0)

    def test_13_partner_total_earned(self):
        """Test: Verificar total de puntos ganados históricamente"""
        # Resetear historial
        self.partner.loyalty_points = 0.0
        self.partner.loyalty_history_ids.unlink()
        
        session = self._create_pos_session(self.pos_config)
        
        # Crear varias órdenes
        for amount in [100.0, 50.0, 75.0]:
            order = self._create_pos_order(session, self.partner, amount)
            self.env['pos.payment'].create({
                'pos_order_id': order.id,
                'amount': amount,
                'payment_method_id': self.payment_method.id,
            })
            order.action_pos_order_paid()
        
        # Total ganado: 10 + 5 + 7 = 22 puntos
        self.partner._compute_loyalty_totals()
        self.assertEqual(self.partner.loyalty_points_total_earned, 22.0)

    def test_14_partner_action_view_history(self):
        """Test: Verificar acción de ver histórico"""
        action = self.partner.action_view_loyalty_history()
        
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'pos.loyalty.history')
        self.assertIn(('partner_id', '=', self.partner.id), action['domain'])

    def test_15_no_points_without_partner(self):
        """Test: No acumular puntos si no hay cliente en la orden"""
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, None, 100.0)  # Sin partner
        
        points = order._calculate_loyalty_points()
        self.assertEqual(points, 0.0)

    def test_16_add_loyalty_points_method(self):
        """Test: Método para añadir puntos manualmente"""
        initial_points = self.partner.loyalty_points
        
        # Añadir puntos con descripción
        history = self.partner._add_loyalty_points(
            points=50.0,
            transaction_type='adjustment',
            description='Ajuste manual de prueba'
        )
        
        self.assertEqual(self.partner.loyalty_points, initial_points + 50.0)
        self.assertEqual(history.points, 50.0)
        self.assertEqual(history.transaction_type, 'adjustment')
        self.assertEqual(history.description, 'Ajuste manual de prueba')
        self.assertEqual(history.balance_after, initial_points + 50.0)

    def test_17_loyalty_history_name_sequence(self):
        """Test: Verificar secuencia de nombres en histórico"""
        session = self._create_pos_session(self.pos_config)
        order = self._create_pos_order(session, self.partner, 100.0)
        
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'amount': 100.0,
            'payment_method_id': self.payment_method.id,
        })
        order.action_pos_order_paid()
        
        last_history = self.partner.loyalty_history_ids.sorted('date', reverse=True)[0]
        self.assertTrue(last_history.name.startswith('FID/'))

