# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ProductCrossSell(models.Model):
    _name = 'product.cross.sell'
    _description = 'Regla de Cross-Selling entre Productos'
    _order = 'sequence, id'

    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
        store=True,
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de prioridad para mostrar las sugerencias',
    )
    source_product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto Origen',
        required=True,
        ondelete='cascade',
        index=True,
        help='Producto que dispara la sugerencia de cross-selling',
    )
    suggested_product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto Sugerido',
        required=True,
        ondelete='cascade',
        index=True,
        help='Producto que se sugiere como complementario',
    )
    bidirectional = fields.Boolean(
        string='Relación Bidireccional',
        default=False,
        help='Si está activo, la relación funciona en ambos sentidos '
             '(A sugiere B y B sugiere A)',
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    description = fields.Text(
        string='Descripción',
        help='Razón o descripción de por qué estos productos son complementarios',
    )

    @api.depends('source_product_tmpl_id', 'suggested_product_tmpl_id')
    def _compute_name(self):
        for record in self:
            if record.source_product_tmpl_id and record.suggested_product_tmpl_id:
                record.name = f"{record.source_product_tmpl_id.name} → {record.suggested_product_tmpl_id.name}"
            else:
                record.name = _('Nueva Regla de Cross-Selling')

    @api.constrains('source_product_tmpl_id', 'suggested_product_tmpl_id')
    def _check_different_products(self):
        """Validar que los productos origen y sugerido sean diferentes"""
        for record in self:
            if record.source_product_tmpl_id == record.suggested_product_tmpl_id:
                raise ValidationError(
                    _('El producto origen y el producto sugerido deben ser diferentes.')
                )

    @api.constrains('source_product_tmpl_id', 'suggested_product_tmpl_id', 'company_id', 'active')
    def _check_unique_relation(self):
        """Validar que no exista una relación duplicada activa"""
        for record in self:
            if record.active:
                existing = self.search([
                    ('source_product_tmpl_id', '=', record.source_product_tmpl_id.id),
                    ('suggested_product_tmpl_id', '=', record.suggested_product_tmpl_id.id),
                    ('company_id', '=', record.company_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id),
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _('Ya existe una regla de cross-selling activa entre estos productos.')
                    )

    @api.model
    def get_cross_sell_products(self, product_tmpl_ids, company_id=None):
        """
        Obtener productos sugeridos para una lista de productos.
        
        :param product_tmpl_ids: Lista de IDs de product.template
        :param company_id: ID de la compañía (opcional)
        :return: recordset de product.template sugeridos
        """
        if not product_tmpl_ids:
            return self.env['product.template']

        if company_id is None:
            company_id = self.env.company.id

        domain = [
            ('active', '=', True),
            ('company_id', '=', company_id),
            '|',
            ('source_product_tmpl_id', 'in', product_tmpl_ids),
            '&',
            ('bidirectional', '=', True),
            ('suggested_product_tmpl_id', 'in', product_tmpl_ids),
        ]

        rules = self.search(domain)

        suggested_products = self.env['product.template']
        
        for rule in rules:
            if rule.source_product_tmpl_id.id in product_tmpl_ids:
                suggested_products |= rule.suggested_product_tmpl_id
            if rule.bidirectional and rule.suggested_product_tmpl_id.id in product_tmpl_ids:
                suggested_products |= rule.source_product_tmpl_id

        # Excluir los productos que ya están en la lista original
        suggested_products = suggested_products.filtered(
            lambda p: p.id not in product_tmpl_ids
        )

        return suggested_products

    def copy(self, default=None):
        """Al duplicar, desactivar por defecto para evitar conflictos"""
        default = dict(default or {})
        default.setdefault('active', False)
        return super().copy(default)

