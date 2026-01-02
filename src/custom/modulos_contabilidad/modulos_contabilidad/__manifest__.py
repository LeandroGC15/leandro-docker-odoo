# -*- coding: utf-8 -*-
{
    'name': 'Módulos Contabilidad',
    'version': '17.0.3.1.0',
    'category': 'Accounting',
    'summary': 'Reglas de descuento automático por tipo de cliente',
    'description': """
        Módulo de Contabilidad para Reglas de Descuento Automático
        ==========================================================
        
        Este módulo permite:
        
        * Crear reglas de descuento (tipos de cliente) desde la interfaz
        * Asignar un tipo a cada cliente
        * Aplicación automática de descuentos en facturas
        
        Incluye por defecto: 
        - Sin tipo (0% - valor por defecto para contactos nuevos)
        - Minorista (5%)
        - Mayorista (10%)
        - VIP (15%)
        
        Los clientes sin tipo asignado (o con "Sin tipo") no reciben descuento.
    """,
    'author': 'Binaural',
    'website': 'https://www.binaural.dev',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/account_discount_rule_data.xml',
        'views/account_discount_rule_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
