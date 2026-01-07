# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extensión de res.partner para agregar campos de fidelización"""
    _inherit = 'res.partner'

    loyalty_points = fields.Float(
        string='Puntos de Fidelización',
        default=0.0,
        help='Puntos de fidelización acumulados por el cliente.',
    )
    loyalty_history_ids = fields.One2many(
        'pos.loyalty.history',
        'partner_id',
        string='Histórico de Puntos',
    )
    loyalty_history_count = fields.Integer(
        string='Transacciones de Puntos',
        compute='_compute_loyalty_history_count',
    )
    loyalty_points_total_earned = fields.Float(
        string='Total Puntos Ganados',
        compute='_compute_loyalty_totals',
        store=True,
        help='Total de puntos ganados históricamente.',
    )
    loyalty_points_total_redeemed = fields.Float(
        string='Total Puntos Canjeados',
        compute='_compute_loyalty_totals',
        store=True,
        help='Total de puntos canjeados históricamente.',
    )

    @api.depends('loyalty_history_ids')
    def _compute_loyalty_history_count(self):
        for partner in self:
            partner.loyalty_history_count = len(partner.loyalty_history_ids)

    @api.depends('loyalty_history_ids.points', 'loyalty_history_ids.transaction_type')
    def _compute_loyalty_totals(self):
        for partner in self:
            earned = sum(
                h.points for h in partner.loyalty_history_ids 
                if h.transaction_type == 'earned'
            )
            redeemed = abs(sum(
                h.points for h in partner.loyalty_history_ids 
                if h.transaction_type == 'redeemed'
            ))
            partner.loyalty_points_total_earned = earned
            partner.loyalty_points_total_redeemed = redeemed

    def action_view_loyalty_history(self):
        """Abrir el histórico de puntos del cliente"""
        self.ensure_one()
        return {
            'name': f'Histórico de Puntos - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.loyalty.history',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_partner_id': self.id,
            },
        }

    def action_print_loyalty_report(self):
        """Imprimir reporte de histórico de puntos del cliente"""
        self.ensure_one()
        return self.env.ref(
            'pos_loyalty_program.action_report_partner_loyalty_history'
        ).report_action(self)

    def _add_loyalty_points(self, points, order=None, transaction_type='earned', description=None):
        """
        Añadir puntos de fidelización al cliente.
        
        Args:
            points: Cantidad de puntos (positivo para ganar, negativo para canjear)
            order: Orden POS relacionada (opcional)
            transaction_type: Tipo de transacción ('earned', 'redeemed', 'adjustment')
            description: Descripción de la transacción (opcional)
        
        Returns:
            El registro de histórico creado
        """
        self.ensure_one()
        
        new_balance = self.loyalty_points + points
        
        # Crear registro de histórico
        history_vals = {
            'partner_id': self.id,
            'order_id': order.id if order else False,
            'date': fields.Datetime.now(),
            'transaction_type': transaction_type,
            'points': points,
            'balance_after': new_balance,
            'order_amount': order.amount_total if order else 0.0,
            'description': description,
        }
        
        history = self.env['pos.loyalty.history'].create(history_vals)
        
        # Actualizar puntos del cliente
        self.loyalty_points = new_balance
        
        _logger.info(
            f"Puntos de fidelización actualizados para {self.name}: "
            f"{points:+.0f} puntos, nuevo saldo: {new_balance:.0f}"
        )
        
        return history

