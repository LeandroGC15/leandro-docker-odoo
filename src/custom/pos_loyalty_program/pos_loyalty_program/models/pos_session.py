# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    """Extensión de pos.session para mostrar resumen de puntos de fidelización"""
    _inherit = 'pos.session'

    loyalty_points_earned = fields.Float(
        string='Puntos Ganados',
        compute='_compute_loyalty_summary',
        store=True,
        help='Total de puntos de fidelización ganados en esta sesión.',
    )
    loyalty_transactions_count = fields.Integer(
        string='Transacciones de Fidelización',
        compute='_compute_loyalty_summary',
        store=True,
        help='Cantidad de órdenes que generaron puntos de fidelización.',
    )

    @api.depends('order_ids.loyalty_points_earned')
    def _compute_loyalty_summary(self):
        for session in self:
            orders_with_points = session.order_ids.filtered(
                lambda o: o.loyalty_points_earned > 0
            )
            session.loyalty_points_earned = sum(orders_with_points.mapped('loyalty_points_earned'))
            session.loyalty_transactions_count = len(orders_with_points)

