# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class PosLoyaltyHistory(models.Model):
    """Modelo para registrar el histórico de transacciones de puntos de fidelización"""
    _name = 'pos.loyalty.history'
    _description = 'Histórico de Puntos de Fidelización'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('pos.loyalty.history') or 'Nuevo',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        index=True,
    )
    order_id = fields.Many2one(
        'pos.order',
        string='Orden POS',
        ondelete='set null',
        index=True,
    )
    session_id = fields.Many2one(
        'pos.session',
        string='Sesión POS',
        related='order_id.session_id',
        store=True,
    )
    date = fields.Datetime(
        string='Fecha',
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    transaction_type = fields.Selection(
        selection=[
            ('earned', 'Ganados'),
            ('redeemed', 'Canjeados'),
            ('adjustment', 'Ajuste'),
        ],
        string='Tipo',
        required=True,
        default='earned',
    )
    points = fields.Float(
        string='Puntos',
        required=True,
        help='Puntos de la transacción. Positivo para ganar, negativo para canjear.',
    )
    balance_after = fields.Float(
        string='Saldo Después',
        required=True,
        help='Saldo de puntos del cliente después de esta transacción.',
    )
    order_amount = fields.Float(
        string='Monto de Orden',
        help='Monto de la orden que generó estos puntos.',
    )
    description = fields.Text(
        string='Descripción',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        related='partner_id.company_id',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('pos.loyalty.history') or 'Nuevo'
        return super().create(vals_list)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} - {record.partner_id.name} ({record.points:+.0f} pts)"
            result.append((record.id, name))
        return result

