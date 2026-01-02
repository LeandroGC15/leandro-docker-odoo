# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

# Constante para los tipos de cliente disponibles
CUSTOMER_TYPE_SELECTION = [
    ('minorista', 'Minorista'),
    ('mayorista', 'Mayorista'),
    ('vip', 'VIP'),
    ('none', 'Sin Tipo'),
]


class AccountDiscountRule(models.Model):
    _name = 'account.discount.rule'
    _description = 'Regla de Descuento por Tipo de Cliente'
    _order = 'customer_type, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre descriptivo de la regla (ej: Descuento VIP 15%)',
    )
    customer_type = fields.Selection(
        selection=CUSTOMER_TYPE_SELECTION,
        string='Tipo de Cliente',
        required=True,
        default='none',
        help='Tipo de cliente al que se aplicará esta regla de descuento',
    )
    discount_percentage = fields.Float(
        string='Porcentaje de Descuento',
        required=True,
        default=0.0,
        digits=(16, 2),
        help='Porcentaje de descuento a aplicar (0-100)',
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    is_default = fields.Boolean(
        string='Regla por Defecto',
        default=False,
        help='Si está marcado, esta regla se usa como valor por defecto para contactos nuevos',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )

    @api.constrains('discount_percentage')
    def _check_discount_percentage(self):
        """Validar que el porcentaje esté entre 0 y 100"""
        for record in self:
            if record.discount_percentage < 0 or record.discount_percentage > 100:
                raise ValidationError(
                    'El porcentaje de descuento debe estar entre 0 y 100.'
                )

    @api.constrains('customer_type', 'company_id', 'active')
    def _check_unique_customer_type(self):
        """Validar que no haya reglas activas duplicadas para el mismo tipo y compañía"""
        for record in self:
            if record.active and record.customer_type != 'none':
                existing = self.search([
                    ('customer_type', '=', record.customer_type),
                    ('company_id', '=', record.company_id.id),
                    ('active', '=', True),
                    ('id', '!=', record.id),
                ], limit=1)
                if existing:
                    type_label = dict(CUSTOMER_TYPE_SELECTION).get(record.customer_type, record.customer_type)
                    raise ValidationError(
                        f'Ya existe una regla activa para el tipo de cliente "{type_label}" '
                        f'en esta compañía: {existing.name}.'
                    )

    @api.constrains('is_default')
    def _check_is_default(self):
        """Solo puede haber una regla por defecto por compañía"""
        for record in self:
            if record.is_default:
                existing = self.search([
                    ('is_default', '=', True),
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id),
                ], limit=1)
                if existing:
                    raise ValidationError(
                        'Ya existe una regla por defecto para esta compañía. '
                        'Solo puede haber una regla marcada como "por defecto".'
                    )

    def name_get(self):
        """Mostrar tipo de cliente con porcentaje"""
        result = []
        for record in self:
            type_label = dict(CUSTOMER_TYPE_SELECTION).get(record.customer_type, record.customer_type)
            if record.discount_percentage > 0:
                name = f"{type_label} ({record.discount_percentage:.0f}%)"
            else:
                name = f"{type_label} - {record.name}"
            result.append((record.id, name))
        return result

    @api.model
    def _get_default_rule(self, company_id=None):
        """Obtener la regla por defecto (Sin tipo)"""
        if company_id is None:
            company_id = self.env.company.id
        return self.search([
            ('is_default', '=', True),
            ('company_id', '=', company_id),
        ], limit=1)

    @api.model
    def _get_discount_for_customer_type(self, customer_type, company_id=None):
        """
        Obtener el porcentaje de descuento para un tipo de cliente.
        
        :param customer_type: Tipo de cliente (minorista, mayorista, vip, none)
        :param company_id: ID de la compañía (opcional, usa la actual si no se especifica)
        :return: Porcentaje de descuento (0 si no se encuentra regla)
        """
        if not customer_type or customer_type == 'none':
            return 0.0

        if company_id is None:
            company_id = self.env.company.id

        rule = self.search([
            ('customer_type', '=', customer_type),
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], limit=1)

        return rule.discount_percentage if rule else 0.0
