# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo relacionado para mostrar el tipo de cliente en la factura
    customer_type = fields.Selection(
        related='partner_id.customer_type',
        string='Tipo de Cliente',
        readonly=True,
        store=False,
    )

    def _get_customer_type(self):
        """Obtener el tipo de cliente del partner de la factura"""
        if not self.partner_id:
            return 'none'
        return self.partner_id.customer_type or 'none'

    def _get_discount_percentage(self):
        """Obtener el porcentaje de descuento según el tipo de cliente"""
        customer_type = self._get_customer_type()
        if customer_type == 'none':
            return 0.0
        
        # Buscar regla por tipo de cliente
        discount_rule_model = self.env['account.discount.rule']
        return discount_rule_model._get_discount_for_customer_type(
            customer_type,
            company_id=self.company_id.id,
        )

    @api.onchange('partner_id')
    def _onchange_partner_id_apply_discounts(self):
        """Aplicar descuentos cuando se cambia el cliente"""
        if self.partner_id and self.move_type in ('out_invoice', 'out_refund'):
            self._apply_automatic_discounts()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids_apply_discounts(self):
        """Aplicar descuentos cuando se modifican las líneas"""
        if self.partner_id and self.move_type in ('out_invoice', 'out_refund'):
            self._apply_automatic_discounts()

    def action_post(self):
        """Aplicar descuentos automáticos antes de validar la factura"""
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund') and move.state == 'draft':
                move._apply_automatic_discounts()
        return super().action_post()

    def _apply_automatic_discounts(self):
        """
        Aplicar descuentos automáticos a las líneas de factura según el tipo de cliente.
        Solo se aplica a facturas de clientes (out_invoice, out_refund).
        """
        if self.move_type not in ('out_invoice', 'out_refund'):
            return

        customer_type = self._get_customer_type()
        if customer_type == 'none':
            _logger.debug(
                'Cliente %s sin tipo definido - no se aplica descuento',
                self.partner_id.name if self.partner_id else 'N/A'
            )
            return

        discount_percentage = self._get_discount_percentage()
        
        if discount_percentage <= 0:
            _logger.debug(
                'Tipo de cliente %s sin descuento configurado para %s',
                customer_type,
                self.partner_id.name if self.partner_id else 'N/A'
            )
            return

        _logger.info(
            'Aplicando descuento automático: %.2f%% (tipo: %s) para cliente %s',
            discount_percentage,
            customer_type,
            self.partner_id.name if self.partner_id else 'N/A'
        )

        for line in self.invoice_line_ids:
            # Solo aplicar a líneas de producto sin descuento previo
            if (
                not line.display_type
                and (line.discount == 0 or line.discount == 0.0)
                and line.product_id
            ):
                line.discount = discount_percentage
                _logger.debug(
                    'Descuento %.2f%% aplicado a línea %s',
                    discount_percentage,
                    line.product_id.name
                )
