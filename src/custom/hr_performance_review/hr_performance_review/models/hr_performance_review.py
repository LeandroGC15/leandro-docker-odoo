# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrPerformanceReview(models.Model):
    _name = 'hr.performance.review'
    _description = 'Evaluación de Desempeño'
    _order = 'review_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo'),
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado Evaluado',
        required=True,
        tracking=True,
        index=True,
    )
    reviewer_id = fields.Many2one(
        'hr.employee',
        string='Evaluador',
        required=True,
        tracking=True,
        help='Empleado que realiza la evaluación',
    )
    review_date = fields.Date(
        string='Fecha de Evaluación',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    score = fields.Float(
        string='Calificación',
        required=True,
        default=0.0,
        tracking=True,
        help='Calificación numérica del 0 al 10',
    )
    score_percentage = fields.Float(
        string='Porcentaje',
        compute='_compute_score_percentage',
        store=True,
        help='Porcentaje de la calificación (para visualización)',
    )
    
    @api.depends('score')
    def _compute_score_percentage(self):
        for record in self:
            record.score_percentage = (record.score / 10.0) * 100.0 if record.score else 0.0
    comments = fields.Text(
        string='Observaciones',
        help='Observaciones cualitativas sobre el desempeño del empleado',
    )
    goals_next_period = fields.Text(
        string='Objetivos para el Siguiente Período',
        help='Metas y objetivos definidos para el próximo ciclo de evaluación',
    )
    strengths = fields.Text(
        string='Fortalezas',
        help='Puntos fuertes identificados en el empleado',
    )
    weaknesses = fields.Text(
        string='Áreas de Mejora',
        help='Aspectos a mejorar identificados en el empleado',
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('done', 'Completada'),
        ('cancel', 'Cancelada'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Departamento',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Puesto de Trabajo',
        related='employee_id.job_id',
        store=True,
        readonly=True,
    )
    
    # Campo computado para color en kanban
    kanban_state = fields.Selection([
        ('normal', 'Gris'),
        ('done', 'Verde'),
        ('blocked', 'Rojo'),
    ], string='Estado Kanban', compute='_compute_kanban_state', store=True)
    
    @api.depends('state')
    def _compute_kanban_state(self):
        for record in self:
            if record.state == 'done':
                record.kanban_state = 'done'
            elif record.state == 'cancel':
                record.kanban_state = 'blocked'
            else:
                record.kanban_state = 'normal'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.performance.review'
                ) or _('Nuevo')
        return super().create(vals_list)

    @api.constrains('score')
    def _check_score(self):
        for record in self:
            if record.score < 0 or record.score > 10:
                raise ValidationError(
                    _('La calificación debe estar entre 0 y 10.')
                )

    @api.constrains('employee_id', 'reviewer_id')
    def _check_different_employee_reviewer(self):
        for record in self:
            if record.employee_id == record.reviewer_id:
                raise ValidationError(
                    _('El empleado evaluado no puede ser su propio evaluador.')
                )

    def action_start_review(self):
        """Iniciar la evaluación"""
        for record in self:
            record.state = 'in_progress'

    def action_complete_review(self):
        """Completar la evaluación"""
        for record in self:
            if record.score == 0:
                raise ValidationError(
                    _('Debe asignar una calificación antes de completar la evaluación.')
                )
            record.state = 'done'

    def action_cancel_review(self):
        """Cancelar la evaluación"""
        for record in self:
            record.state = 'cancel'

    def action_reset_to_draft(self):
        """Volver a borrador"""
        for record in self:
            record.state = 'draft'

    def action_print_report(self):
        """Imprimir reporte de evaluación"""
        return self.env.ref(
            'hr_performance_review.action_report_performance_review'
        ).report_action(self)

