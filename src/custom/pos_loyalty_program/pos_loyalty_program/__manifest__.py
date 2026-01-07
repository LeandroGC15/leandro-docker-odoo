# -*- coding: utf-8 -*-
{
    'name': 'Punto de Venta - Programa de Fidelización',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Sistema de puntos de fidelización para clientes en POS',
    'description': """
        Módulo de Programa de Fidelización para Punto de Venta
        =======================================================
        
        Este módulo permite:
        
        * Acumular puntos de fidelización para clientes en ventas POS
        * Configurar la tasa de acumulación de puntos (ej: 1 punto por cada $10)
        * Ver el resumen de puntos acumulados por sesión
        * Consultar el histórico de puntos por cliente
        * Generar reportes PDF con el historial de fidelización
        
        Configuración:
        - Habilitar el programa en Configuración de Punto de Venta
        - Definir puntos por monto gastado
        - Seleccionar tipo de redondeo de puntos
        
        Flujo de trabajo:
        - El cliente compra en el POS
        - Al validar la orden, se calculan los puntos según el monto
        - Los puntos se acumulan en el cliente
        - Se registra la transacción en el histórico
    """,
    'author': 'Binaural',
    'website': 'https://www.binaural.dev',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/res_partner_views.xml',
        'views/pos_session_views.xml',
        'views/pos_loyalty_history_views.xml',
        'report/pos_loyalty_report.xml',
        'report/pos_loyalty_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

