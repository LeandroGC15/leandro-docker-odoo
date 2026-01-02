# -*- coding: utf-8 -*-
{
    'name': 'RRHH - Evaluaciones de Desempeño',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Flujo de evaluaciones periódicas para empleados',
    'description': """
        Módulo de Evaluaciones de Desempeño para RRHH
        ==============================================
        
        Este módulo permite:
        
        * Crear evaluaciones de desempeño para empleados
        * Asignar evaluadores y fechas de revisión
        * Registrar calificaciones numéricas y observaciones cualitativas
        * Definir fortalezas, debilidades y objetivos para el siguiente período
        * Seguimiento por estado (pendiente, en progreso, completada)
        * Reportes PDF con histórico de evaluaciones por empleado
        
        Flujo de trabajo:
        - Borrador: Evaluación creada pero no iniciada
        - En Progreso: Evaluación en proceso de revisión
        - Completada: Evaluación finalizada
        - Cancelada: Evaluación cancelada
    """,
    'author': 'Binaural',
    'website': 'https://www.binaural.dev',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_performance_review_views.xml',
        'views/hr_employee_views.xml',
        'report/hr_performance_review_report.xml',
        'report/hr_performance_review_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

