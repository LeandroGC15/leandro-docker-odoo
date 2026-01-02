# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class CrossSellWizard(models.TransientModel):
    _name = 'cross.sell.wizard'
    _description = 'Wizard de Sugerencias de Cross-Selling'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido de Venta',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    line_ids = fields.One2many(
        'cross.sell.wizard.line',
        'wizard_id',
        string='Productos Sugeridos',
    )
    selected_count = fields.Integer(
        string='Productos Seleccionados',
        compute='_compute_selected_count',
    )

    @api.depends('line_ids.selected')
    def _compute_selected_count(self):
        for wizard in self:
            wizard.selected_count = len(wizard.line_ids.filtered('selected'))

    def action_add_selected_products(self):
        """Añadir productos seleccionados al pedido de venta"""
        self.ensure_one()
        
        selected_lines = self.line_ids.filtered('selected')
        
        if not selected_lines:
            raise UserError(_('Por favor, seleccione al menos un producto para añadir.'))

        order = self.sale_order_id
        
        if order.state not in ('draft', 'sent'):
            raise UserError(
                _('Solo puede añadir productos a pedidos en estado borrador o enviado.')
            )

        added_products = []
        
        for line in selected_lines:
            # Obtener el primer variante del producto template
            product = line.product_tmpl_id.product_variant_id
            if not product:
                product = line.product_tmpl_id.product_variant_ids[:1]
            
            if product:
                # En Odoo 17, crear la línea directamente con los valores mínimos
                # Los campos computados se calculan automáticamente
                order_line_vals = {
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': line.quantity,
                }
                
                self.env['sale.order.line'].with_context(
                    skip_cross_sell_check=True
                ).create(order_line_vals)
                
                added_products.append(product.display_name)
                _logger.info(
                    f"Cross-selling: Producto '{product.display_name}' añadido al pedido {order.name}"
                )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Productos añadidos'),
                'message': _('Se añadieron %d producto(s) al pedido: %s') % (
                    len(added_products),
                    ', '.join(added_products[:3]) + ('...' if len(added_products) > 3 else '')
                ),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_select_all(self):
        """Seleccionar todos los productos"""
        self.ensure_one()
        self.line_ids.write({'selected': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cross.sell.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_deselect_all(self):
        """Deseleccionar todos los productos"""
        self.ensure_one()
        self.line_ids.write({'selected': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cross.sell.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class CrossSellWizardLine(models.TransientModel):
    _name = 'cross.sell.wizard.line'
    _description = 'Línea de Wizard de Cross-Selling'
    _order = 'sequence, id'

    wizard_id = fields.Many2one(
        'cross.sell.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto',
        required=True,
    )
    product_name = fields.Char(
        string='Nombre del Producto',
        related='product_tmpl_id.name',
        readonly=True,
    )
    product_default_code = fields.Char(
        string='Referencia Interna',
        related='product_tmpl_id.default_code',
        readonly=True,
    )
    product_list_price = fields.Float(
        string='Precio de Venta',
        related='product_tmpl_id.list_price',
        readonly=True,
    )
    product_image = fields.Binary(
        string='Imagen',
        related='product_tmpl_id.image_128',
        readonly=True,
    )
    selected = fields.Boolean(
        string='Seleccionado',
        default=False,
    )
    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='wizard_id.sale_order_id.currency_id',
        readonly=True,
    )

