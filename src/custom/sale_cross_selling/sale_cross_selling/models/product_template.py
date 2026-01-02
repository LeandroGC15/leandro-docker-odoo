# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cross_sell_ids = fields.One2many(
        'product.cross.sell',
        'source_product_tmpl_id',
        string='Productos Cross-Selling',
        help='Productos sugeridos como complementarios cuando se vende este producto',
    )
    cross_sell_count = fields.Integer(
        string='Número de Cross-Sells',
        compute='_compute_cross_sell_count',
        store=True,
    )

    @api.depends('cross_sell_ids')
    def _compute_cross_sell_count(self):
        for record in self:
            record.cross_sell_count = len(record.cross_sell_ids.filtered('active'))

    def action_view_cross_sell_rules(self):
        """Abrir vista de reglas de cross-selling del producto"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reglas de Cross-Selling',
            'res_model': 'product.cross.sell',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                ('source_product_tmpl_id', '=', self.id),
                '&',
                ('bidirectional', '=', True),
                ('suggested_product_tmpl_id', '=', self.id),
            ],
            'context': {
                'default_source_product_tmpl_id': self.id,
            },
        }

    def action_add_cross_sell(self):
        """Acción rápida para añadir una nueva regla de cross-selling"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Regla de Cross-Selling',
            'res_model': 'product.cross.sell',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_product_tmpl_id': self.id,
            },
        }

