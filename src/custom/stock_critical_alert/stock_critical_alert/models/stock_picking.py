# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPickingCountryCode(models.Model):
    """
    Extensión para agregar el campo country_code a stock.picking.
    Este campo es requerido por la vista stock.valuation.layer.picking
    del módulo stock_account en Odoo 17.
    """
    _inherit = 'stock.picking'
    
    country_code = fields.Char(
        string='Country Code',
        related='company_id.country_id.code',
        readonly=True,
    )
