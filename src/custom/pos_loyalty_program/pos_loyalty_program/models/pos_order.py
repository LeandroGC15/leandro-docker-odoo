# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math

import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """Extensión de pos.order para calcular y asignar puntos de fidelización"""
    _inherit = 'pos.order'

    loyalty_points_earned = fields.Float(
        string='Puntos Ganados',
        default=0.0,
        readonly=True,
        help='Puntos de fidelización ganados en esta orden.',
    )

    def _calculate_loyalty_points(self):
        """
        Calcular los puntos de fidelización para esta orden.
        
        Returns:
            float: Puntos calculados según la configuración del POS
        """
        self.ensure_one()
        
        config = self.config_id
        
        # Verificar si el programa está habilitado
        if not config.loyalty_program_enabled:
            return 0.0
        
        # Verificar que hay un cliente
        if not self.partner_id:
            return 0.0
        
        # Verificar configuración válida
        if config.loyalty_amount_per_points <= 0:
            return 0.0
        
        # Calcular puntos base
        # Fórmula: (monto_total / monto_por_punto) * puntos_por_unidad
        points_raw = (self.amount_total / config.loyalty_amount_per_points) * config.loyalty_points_per_amount
        
        # Aplicar redondeo según configuración
        if config.loyalty_points_rounding == 'floor':
            points = math.floor(points_raw)
        elif config.loyalty_points_rounding == 'ceiling':
            points = math.ceil(points_raw)
        else:  # nearest
            points = round(points_raw)
        
        return max(0.0, float(points))

    def action_pos_order_paid(self):
        """
        Sobrescribir para calcular y asignar puntos de fidelización al validar el pago.
        """
        result = super().action_pos_order_paid()
        
        for order in self:
            order._assign_loyalty_points()
        
        return result

    def _assign_loyalty_points(self):
        """
        Calcular y asignar puntos de fidelización al cliente.
        """
        self.ensure_one()
        
        # Calcular puntos
        points = self._calculate_loyalty_points()
        
        if points > 0 and self.partner_id:
            # Registrar puntos en la orden
            self.loyalty_points_earned = points
            
            # Añadir puntos al cliente con histórico
            description = f"Puntos por compra en {self.config_id.name} - Orden {self.name}"
            self.partner_id._add_loyalty_points(
                points=points,
                order=self,
                transaction_type='earned',
                description=description,
            )
            
            _logger.info(
                f"Orden {self.name}: {points:.0f} puntos asignados a {self.partner_id.name}"
            )

