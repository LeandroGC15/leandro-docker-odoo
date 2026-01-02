# -*- coding: utf-8 -*-
{
    'name': 'Ventas - Reglas de Cross-Selling',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Sugerir productos complementarios en pedidos de venta',
    'description': """
        Módulo de Cross-Selling para Ventas
        ====================================
        
        Este módulo permite:
        
        * Definir relaciones de cross-selling entre productos
        * Al añadir un producto en un pedido de venta, sugerir productos complementarios
        * Mostrar sugerencias mediante un wizard interactivo
        * Añadir productos sugeridos directamente al pedido
        
        Flujo de trabajo:
        - Configurar relaciones de productos (Producto A sugiere Producto B)
        - Al crear/editar un pedido de venta, añadir productos
        - El sistema muestra automáticamente sugerencias de productos complementarios
        - El usuario puede seleccionar qué productos añadir al pedido
        
        Configuración:
        - Accesible desde el menú de Ventas > Configuración > Cross-Selling
    """,
    'author': 'Binaural',
    'website': 'https://www.binaural.dev',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_cross_sell_views.xml',
        'views/product_template_views.xml',
        'wizard/cross_sell_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

