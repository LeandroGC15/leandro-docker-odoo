# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_minimum = fields.Float(
        string='Stock Mínimo',
        default=0.0,
        help='Cantidad mínima de stock. Se generará una alerta cuando el stock '
             'disponible caiga por debajo de este valor.',
    )
    is_stock_critical = fields.Boolean(
        string='Stock Crítico',
        compute='_compute_is_stock_critical',
        search='_search_is_stock_critical',
        help='Indica si el stock actual está por debajo del mínimo configurado',
    )
    stock_alert_ids = fields.One2many(
        'stock.critical.alert',
        'product_tmpl_id',
        string='Alertas de Stock',
    )
    stock_alert_count = fields.Integer(
        string='Número de Alertas',
        compute='_compute_stock_alert_count',
    )

    @api.depends('qty_available', 'stock_minimum')
    def _compute_is_stock_critical(self):
        for product in self:
            product.is_stock_critical = (
                product.stock_minimum > 0 and 
                product.qty_available < product.stock_minimum
            )

    def _search_is_stock_critical(self, operator, value):
        """Búsqueda para el campo calculado is_stock_critical"""
        if operator not in ('=', '!='):
            raise ValueError('Operador no soportado para is_stock_critical')
        
        # Obtener todos los productos con stock mínimo configurado
        products = self.search([('stock_minimum', '>', 0)])
        critical_product_ids = products.filtered(
            lambda p: p.qty_available < p.stock_minimum
        ).ids
        
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', critical_product_ids)]
        else:
            return [('id', 'not in', critical_product_ids)]

    def _compute_stock_alert_count(self):
        for product in self:
            product.stock_alert_count = len(product.stock_alert_ids)

    def action_view_stock_alerts(self):
        """Abrir vista de alertas de stock del producto"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Alertas de Stock',
            'res_model': 'stock.critical.alert',
            'view_mode': 'tree,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {
                'default_product_tmpl_id': self.id,
            },
        }

    def check_stock_and_alert(self):
        """Verificar stock y generar alerta si es necesario"""
        self.ensure_one()
        if self.is_stock_critical:
            self.env['stock.critical.alert'].create_alert_if_not_exists(self)

