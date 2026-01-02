# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_apply_discount(self):
        """Aplicar descuento automático cuando se selecciona un producto"""
        if self.product_id and self.move_id:
            # Solo aplicar a facturas de cliente en borrador
            if (
                self.move_id.move_type in ('out_invoice', 'out_refund')
                and not self.discount
            ):
                discount = self.move_id._get_discount_percentage()
                if discount > 0:
                    self.discount = discount
                    _logger.info(
                        'Descuento automático aplicado (onchange): %.2f%% para producto %s',
                        discount,
                        self.product_id.name
                    )

    @api.model_create_multi
    def create(self, vals_list):
        """Aplicar descuento automático al crear líneas de factura"""
        # Aplicar descuento ANTES de crear la línea
        for vals in vals_list:
            if vals.get('move_id') and vals.get('product_id') and not vals.get('discount'):
                move = self.env['account.move'].browse(vals['move_id'])
                if move.move_type in ('out_invoice', 'out_refund') and move.state == 'draft':
                    discount = move._get_discount_percentage()
                    if discount > 0:
                        vals['discount'] = discount
                        _logger.info(
                            'Descuento automático aplicado (create): %.2f%% para producto_id=%s',
                            discount,
                            vals.get('product_id')
                        )
        return super().create(vals_list)

