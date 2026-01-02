# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_cross_sell_suggestions = fields.Boolean(
        string='Tiene Sugerencias Cross-Selling',
        compute='_compute_has_cross_sell_suggestions',
        store=False,
    )

    @api.depends('order_line.product_template_id')
    def _compute_has_cross_sell_suggestions(self):
        CrossSell = self.env['product.cross.sell']
        for order in self:
            product_tmpl_ids = order.order_line.mapped('product_template_id').ids
            if product_tmpl_ids:
                # Obtener productos ya en el pedido
                current_products = set(product_tmpl_ids)
                # Obtener sugerencias
                suggestions = CrossSell.get_cross_sell_products(
                    product_tmpl_ids, 
                    order.company_id.id
                )
                # Filtrar sugerencias que ya están en el pedido
                new_suggestions = suggestions.filtered(
                    lambda p: p.id not in current_products
                )
                order.has_cross_sell_suggestions = bool(new_suggestions)
            else:
                order.has_cross_sell_suggestions = False

    def action_show_cross_sell_wizard(self):
        """Mostrar wizard con sugerencias de cross-selling"""
        self.ensure_one()
        
        product_tmpl_ids = self.order_line.mapped('product_template_id').ids
        if not product_tmpl_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sin productos'),
                    'message': _('Añade productos al pedido para ver sugerencias de cross-selling.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        CrossSell = self.env['product.cross.sell']
        suggestions = CrossSell.get_cross_sell_products(
            product_tmpl_ids,
            self.company_id.id
        )

        # Filtrar sugerencias que ya están en el pedido
        current_products = set(product_tmpl_ids)
        new_suggestions = suggestions.filtered(
            lambda p: p.id not in current_products
        )

        if not new_suggestions:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sin sugerencias'),
                    'message': _('No hay productos complementarios disponibles para los productos actuales.'),
                    'type': 'info',
                    'sticky': False,
                }
            }

        # Crear wizard con las sugerencias
        wizard = self.env['cross.sell.wizard'].create({
            'sale_order_id': self.id,
        })
        
        # Crear líneas del wizard
        for product in new_suggestions:
            self.env['cross.sell.wizard.line'].create({
                'wizard_id': wizard.id,
                'product_tmpl_id': product.id,
                'selected': False,
                'quantity': 1.0,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Productos Complementarios Sugeridos'),
            'res_model': 'cross.sell.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'context': self.env.context,
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        """Al crear líneas de pedido, verificar si hay sugerencias de cross-selling"""
        lines = super().create(vals_list)
        
        # Agrupar líneas por pedido
        orders = lines.mapped('order_id')
        
        for order in orders:
            if order.state in ('draft', 'sent'):
                # Verificar si hay sugerencias disponibles
                product_tmpl_ids = order.order_line.mapped('product_template_id').ids
                if product_tmpl_ids:
                    CrossSell = self.env['product.cross.sell']
                    suggestions = CrossSell.get_cross_sell_products(
                        product_tmpl_ids,
                        order.company_id.id
                    )
                    
                    current_products = set(product_tmpl_ids)
                    new_suggestions = suggestions.filtered(
                        lambda p: p.id not in current_products
                    )
                    
                    if new_suggestions:
                        _logger.info(
                            f"Cross-selling: Se encontraron {len(new_suggestions)} "
                            f"sugerencias para el pedido {order.name}"
                        )

        return lines

