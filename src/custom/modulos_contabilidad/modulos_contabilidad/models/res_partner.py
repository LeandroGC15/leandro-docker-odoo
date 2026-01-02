# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    discount_rule_id = fields.Many2one(
        comodel_name='account.discount.rule',
        string='Regla de Descuento',
        help='Regla de descuento que se aplicará automáticamente en las facturas',
        tracking=True,
        default=lambda self: self._get_default_discount_rule(),
    )

    # Campo relacionado para facilitar filtrado por tipo de cliente
    customer_type = fields.Selection(
        related='discount_rule_id.customer_type',
        string='Tipo de Cliente',
        store=True,
        readonly=True,
        help='Tipo de cliente derivado de la regla de descuento asignada',
    )

    @api.model
    def _get_default_discount_rule(self):
        """Obtener la regla por defecto (Sin tipo)"""
        rule_model = self.env['account.discount.rule']
        default_rule = rule_model._get_default_rule()
        return default_rule.id if default_rule else False
