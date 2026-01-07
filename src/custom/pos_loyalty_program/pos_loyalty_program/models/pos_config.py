# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Extensión de pos.config para configuración del programa de fidelización"""
    _inherit = 'pos.config'

    loyalty_program_enabled = fields.Boolean(
        string='Habilitar Programa de Fidelización',
        default=False,
        help='Activar el sistema de puntos de fidelización para este punto de venta.',
    )
    loyalty_points_per_amount = fields.Float(
        string='Puntos a Otorgar',
        default=1.0,
        help='Cantidad de puntos que se otorgan por cada unidad de monto configurada.',
    )
    loyalty_amount_per_points = fields.Float(
        string='Monto por Punto',
        default=10.0,
        help='Monto de compra requerido para otorgar los puntos configurados. '
             'Ejemplo: Si es 10, se otorga 1 punto por cada $10 de compra.',
    )
    loyalty_points_rounding = fields.Selection(
        selection=[
            ('floor', 'Redondear hacia abajo'),
            ('ceiling', 'Redondear hacia arriba'),
            ('nearest', 'Redondear al más cercano'),
        ],
        string='Tipo de Redondeo',
        default='floor',
        help='Cómo redondear los puntos calculados:\n'
             '- Hacia abajo: 1.9 puntos = 1 punto\n'
             '- Hacia arriba: 1.1 puntos = 2 puntos\n'
             '- Al más cercano: 1.4 = 1 punto, 1.5 = 2 puntos',
    )

    @api.constrains('loyalty_points_per_amount', 'loyalty_amount_per_points')
    def _check_loyalty_config(self):
        for config in self:
            if config.loyalty_program_enabled:
                if config.loyalty_points_per_amount <= 0:
                    continue  # Allow 0 or negative to effectively disable
                if config.loyalty_amount_per_points <= 0:
                    from odoo.exceptions import ValidationError
                    raise ValidationError(
                        'El monto por punto debe ser mayor a 0 cuando el programa está habilitado.'
                    )

