# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockCriticalAlert(models.Model):
    _name = 'stock.critical.alert'
    _description = 'Alerta de Stock Crítico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Producto',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Variante de Producto',
        compute='_compute_product_id',
        store=True,
    )
    category_id = fields.Many2one(
        'product.category',
        string='Categoría',
        related='product_tmpl_id.categ_id',
        store=True,
        readonly=True,
    )
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True,
    )
    state = fields.Selection([
        ('open', 'Abierta'),
        ('resolved', 'Resuelta'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='open', tracking=True)
    
    stock_minimum = fields.Float(
        string='Stock Mínimo',
        related='product_tmpl_id.stock_minimum',
        readonly=True,
    )
    qty_available_at_alert = fields.Float(
        string='Stock al Momento de Alerta',
        readonly=True,
        help='Cantidad disponible cuando se generó la alerta',
    )
    current_qty_available = fields.Float(
        string='Stock Actual',
        related='product_tmpl_id.qty_available',
        readonly=True,
    )
    deficit = fields.Float(
        string='Déficit',
        compute='_compute_deficit',
        store=True,
        help='Diferencia entre el stock mínimo y el stock actual',
    )
    resolution_date = fields.Datetime(
        string='Fecha de Resolución',
        readonly=True,
    )
    resolution_notes = fields.Text(
        string='Notas de Resolución',
    )
    active = fields.Boolean(
        default=True,
        string='Activo',
    )

    @api.depends('product_tmpl_id')
    def _compute_product_id(self):
        for record in self:
            # Obtener la primera variante del producto
            record.product_id = record.product_tmpl_id.product_variant_id

    @api.depends('product_tmpl_id', 'product_tmpl_id.name', 'create_date')
    def _compute_display_name(self):
        for record in self:
            if record.product_tmpl_id and record.create_date:
                record.display_name = _(
                    'Alerta: %(product)s - %(date)s',
                    product=record.product_tmpl_id.name,
                    date=record.create_date.strftime('%Y-%m-%d %H:%M')
                )
            elif record.product_tmpl_id:
                record.display_name = _('Alerta: %s') % record.product_tmpl_id.name
            else:
                record.display_name = _('Nueva Alerta')

    @api.depends('stock_minimum', 'current_qty_available')
    def _compute_deficit(self):
        for record in self:
            record.deficit = record.stock_minimum - record.current_qty_available

    @api.model
    def create_alert_if_not_exists(self, product_tmpl):
        """
        Crea una alerta para el producto si no existe una alerta abierta.
        Evita duplicados verificando alertas existentes.
        """
        # Verificar si ya existe una alerta abierta para este producto
        existing_alert = self.search([
            ('product_tmpl_id', '=', product_tmpl.id),
            ('state', '=', 'open'),
            ('active', '=', True),
        ], limit=1)
        
        if existing_alert:
            # Ya existe una alerta abierta, no crear duplicado
            return existing_alert
        
        # Crear nueva alerta
        alert = self.create({
            'product_tmpl_id': product_tmpl.id,
            'qty_available_at_alert': product_tmpl.qty_available,
        })
        
        # Generar notificación mail.message
        alert._send_alert_notification()
        
        return alert

    def _send_alert_notification(self):
        """Envía notificación de alerta vía mail.message"""
        self.ensure_one()
        
        message_body = _(
            '<p><strong>⚠️ Alerta de Stock Crítico</strong></p>'
            '<p>El producto <strong>%(product)s</strong> tiene stock bajo:</p>'
            '<ul>'
            '<li>Stock Actual: <strong>%(current)s</strong></li>'
            '<li>Stock Mínimo: <strong>%(minimum)s</strong></li>'
            '<li>Déficit: <strong>%(deficit)s</strong></li>'
            '<li>Categoría: %(category)s</li>'
            '</ul>'
            '<p>Se requiere reabastecimiento.</p>',
            product=self.product_tmpl_id.name,
            current=self.qty_available_at_alert,
            minimum=self.stock_minimum,
            deficit=self.stock_minimum - self.qty_available_at_alert,
            category=self.category_id.complete_name or 'Sin categoría',
        )
        
        # Publicar mensaje en el chatter de la alerta
        self.message_post(
            body=message_body,
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        
        # También publicar en el producto
        if self.product_tmpl_id:
            self.product_tmpl_id.message_post(
                body=message_body,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )

    def action_resolve(self):
        """Marcar alerta como resuelta"""
        self.write({
            'state': 'resolved',
            'resolution_date': fields.Datetime.now(),
        })
        for record in self:
            record.message_post(
                body=_('Alerta resuelta'),
                message_type='notification',
            )

    def action_cancel(self):
        """Cancelar alerta"""
        self.write({
            'state': 'cancelled',
        })
        for record in self:
            record.message_post(
                body=_('Alerta cancelada'),
                message_type='notification',
            )

    def action_reopen(self):
        """Reabrir alerta"""
        self.write({
            'state': 'open',
            'resolution_date': False,
        })

    def action_view_product(self):
        """Ver el producto asociado a la alerta"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.product_tmpl_id.name,
            'res_model': 'product.template',
            'res_id': self.product_tmpl_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _cron_check_stock_alerts(self):
        """
        Método ejecutado por cron para verificar el stock de todos los productos
        y generar alertas cuando sea necesario.
        """
        # Buscar productos con stock mínimo configurado
        products = self.env['product.template'].search([
            ('stock_minimum', '>', 0),
            ('type', '=', 'product'),  # Solo productos almacenables
        ])
        
        alerts_created = 0
        for product in products:
            if product.qty_available < product.stock_minimum:
                alert = self.create_alert_if_not_exists(product)
                if alert and alert.create_date == fields.Datetime.now():
                    alerts_created += 1
        
        # Auto-resolver alertas cuando el stock se normaliza
        open_alerts = self.search([('state', '=', 'open')])
        for alert in open_alerts:
            if alert.product_tmpl_id.qty_available >= alert.stock_minimum:
                alert.write({
                    'state': 'resolved',
                    'resolution_date': fields.Datetime.now(),
                    'resolution_notes': _('Resuelto automáticamente: stock normalizado'),
                })
        
        return alerts_created

    @api.model
    def get_critical_products_dashboard_data(self):
        """Obtener datos para el dashboard de productos críticos"""
        alerts = self.search([('state', '=', 'open')])
        
        # Agrupar por categoría
        categories = {}
        for alert in alerts:
            cat_name = alert.category_id.complete_name or 'Sin categoría'
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append({
                'id': alert.id,
                'product': alert.product_tmpl_id.name,
                'current_stock': alert.current_qty_available,
                'minimum_stock': alert.stock_minimum,
                'deficit': alert.deficit,
            })
        
        return categories

