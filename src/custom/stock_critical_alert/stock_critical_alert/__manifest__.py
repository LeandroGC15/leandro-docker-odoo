# -*- coding: utf-8 -*-
{
    'name': 'Inventario - Alertas de Stock Crítico',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Generar alertas cuando el stock cae por debajo del umbral mínimo',
    'description': """
        Módulo de Alertas de Stock Crítico
        ===================================
        
        Este módulo permite:
        
        * Definir un stock mínimo por producto
        * Generación automática de alertas cuando el stock disponible
          cae por debajo del umbral configurado
        * Notificaciones vía mail.message a usuarios responsables
        * Vista de tablero con productos en estado crítico agrupados por categoría
        * Evita duplicados de alertas para el mismo producto
        
        Flujo de trabajo:
        - Configurar el campo "Stock Mínimo" en cada producto
        - El sistema verifica automáticamente mediante cron job
        - Se generan alertas/notificaciones cuando el stock está bajo
        - Dashboard para monitoreo de productos críticos
        
        Configuración:
        - Accesible desde Inventario > Configuración > Alertas de Stock
    """,
    'author': 'Binaural',
    'website': 'https://www.binaural.dev',
    'depends': ['base', 'stock', 'mail', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/product_template_views.xml',
        'views/stock_critical_alert_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

