# -*- coding: utf-8 -*-
# [ADD] campos para el historial de evaluaciones de desempeño
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    performance_review_ids = fields.One2many(
        'hr.performance.review',
        'employee_id',
        string='Evaluaciones de Desempeño',
    )
    performance_review_count = fields.Integer(
        string='Cantidad de Evaluaciones',
        compute='_compute_performance_review_count',
    )
    last_review_date = fields.Date(
        string='Última Evaluación',
        compute='_compute_last_review',
        store=True,
    )
    last_review_score = fields.Float(
        string='Última Calificación',
        compute='_compute_last_review',
        store=True,
    )
    average_score = fields.Float(
        string='Promedio de Calificación',
        compute='_compute_average_score',
        store=True,
        help='Promedio de todas las evaluaciones completadas',
    )
    average_score_percentage = fields.Float(
        string='Promedio (%)',
        compute='_compute_average_score',
        store=True,
        help='Porcentaje del promedio de calificación (para visualización)',
    )

    @api.depends('performance_review_ids')
    def _compute_performance_review_count(self):
        for employee in self:
            employee.performance_review_count = len(employee.performance_review_ids)

    @api.depends('performance_review_ids.state', 'performance_review_ids.review_date', 'performance_review_ids.score')
    def _compute_last_review(self):
        for employee in self:
            completed_reviews = employee.performance_review_ids.filtered(
                lambda r: r.state == 'done'
            ).sorted('review_date', reverse=True)
            if completed_reviews:
                last_review = completed_reviews[0]
                employee.last_review_date = last_review.review_date
                employee.last_review_score = last_review.score
            else:
                employee.last_review_date = False
                employee.last_review_score = 0.0

    @api.depends('performance_review_ids.state', 'performance_review_ids.score')
    def _compute_average_score(self):
        for employee in self:
            completed_reviews = employee.performance_review_ids.filtered(
                lambda r: r.state == 'done'
            )
            if completed_reviews:
                total_score = sum(completed_reviews.mapped('score'))
                avg = total_score / len(completed_reviews)
                employee.average_score = avg
                employee.average_score_percentage = (avg / 10.0) * 100.0
            else:
                employee.average_score = 0.0
                employee.average_score_percentage = 0.0

    def action_view_performance_reviews(self):
        """Abrir las evaluaciones de desempeño del empleado"""
        self.ensure_one()
        return {
            'name': f'Evaluaciones de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.performance.review',
            'view_mode': 'tree,kanban,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'search_default_employee_id': self.id,
            },
        }
    
    def action_print_performance_history(self):
        """Imprimir reporte histórico de evaluaciones del empleado"""
        self.ensure_one()
        return self.env.ref(
            'hr_performance_review.action_report_employee_performance_history'
        ).report_action(self)

