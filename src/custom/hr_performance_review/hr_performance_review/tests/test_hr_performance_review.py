# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestHrPerformanceReview(TransactionCase):
    """Pruebas para el modelo hr.performance.review"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_model = cls.env['hr.employee']
        cls.review_model = cls.env['hr.performance.review']
        
        # Crear departamento
        cls.department = cls.env['hr.department'].create({
            'name': 'Departamento de Pruebas',
        })
        
        # Crear empleados de prueba
        cls.employee1 = cls.employee_model.create({
            'name': 'Empleado de Prueba 1',
            'department_id': cls.department.id,
        })
        cls.employee2 = cls.employee_model.create({
            'name': 'Empleado de Prueba 2 (Evaluador)',
            'department_id': cls.department.id,
        })
        cls.employee3 = cls.employee_model.create({
            'name': 'Empleado de Prueba 3',
            'department_id': cls.department.id,
        })

    def test_01_create_performance_review(self):
        """Test: Crear evaluación de desempeño válida"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 8.5,
            'comments': 'Excelente desempeño durante el período',
            'strengths': 'Trabajo en equipo, comunicación',
            'weaknesses': 'Gestión del tiempo',
            'goals_next_period': 'Mejorar puntualidad en entregas',
        })
        
        self.assertTrue(review.id)
        self.assertEqual(review.state, 'draft')
        self.assertEqual(review.employee_id, self.employee1)
        self.assertEqual(review.reviewer_id, self.employee2)
        self.assertEqual(review.score, 8.5)

    def test_02_review_name_sequence(self):
        """Test: Verificar que se genera secuencia automática"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 7.0,
        })
        
        # El nombre no debería ser 'Nuevo' después de crear
        self.assertNotEqual(review.name, 'Nuevo')
        self.assertTrue(review.name.startswith('EVAL/'))

    def test_03_score_validation_range(self):
        """Test: Validar que la calificación esté entre 0 y 10"""
        # Calificación válida
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 5.0,
        })
        self.assertEqual(review.score, 5.0)

        # Calificación negativa (inválida)
        with self.assertRaises(ValidationError):
            self.review_model.create({
                'employee_id': self.employee1.id,
                'reviewer_id': self.employee2.id,
                'review_date': date.today(),
                'score': -1.0,
            })

        # Calificación mayor a 10 (inválida)
        with self.assertRaises(ValidationError):
            self.review_model.create({
                'employee_id': self.employee1.id,
                'reviewer_id': self.employee2.id,
                'review_date': date.today(),
                'score': 11.0,
            })

    def test_04_employee_cannot_self_review(self):
        """Test: El empleado no puede ser su propio evaluador"""
        with self.assertRaises(ValidationError):
            self.review_model.create({
                'employee_id': self.employee1.id,
                'reviewer_id': self.employee1.id,  # Mismo empleado como evaluador
                'review_date': date.today(),
                'score': 8.0,
            })

    def test_05_workflow_state_transitions(self):
        """Test: Verificar transiciones de estado del flujo de trabajo"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 7.5,
        })
        
        # Estado inicial: borrador
        self.assertEqual(review.state, 'draft')
        
        # Transición a en progreso
        review.action_start_review()
        self.assertEqual(review.state, 'in_progress')
        
        # Transición a completada
        review.action_complete_review()
        self.assertEqual(review.state, 'done')

    def test_06_cannot_complete_without_score(self):
        """Test: No se puede completar evaluación sin calificación"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 0.0,  # Sin calificación
        })
        
        review.action_start_review()
        
        # Intentar completar sin calificación
        with self.assertRaises(ValidationError):
            review.action_complete_review()

    def test_07_cancel_and_reset_workflow(self):
        """Test: Cancelar y reiniciar evaluación"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 6.0,
        })
        
        # Cancelar desde borrador
        review.action_cancel_review()
        self.assertEqual(review.state, 'cancel')
        
        # Volver a borrador
        review.action_reset_to_draft()
        self.assertEqual(review.state, 'draft')

    def test_08_employee_review_relation(self):
        """Test: Relación entre empleado y evaluaciones"""
        # Crear múltiples evaluaciones para un empleado
        review1 = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 7.0,
        })
        review2 = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee3.id,
            'review_date': date.today(),
            'score': 8.0,
        })
        
        # Verificar contador
        self.assertEqual(self.employee1.performance_review_count, 2)
        
        # Verificar que están en la lista
        self.assertIn(review1, self.employee1.performance_review_ids)
        self.assertIn(review2, self.employee1.performance_review_ids)

    def test_09_employee_average_score(self):
        """Test: Cálculo de promedio de calificación del empleado"""
        # Crear evaluaciones completadas
        review1 = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 6.0,
        })
        review1.action_start_review()
        review1.action_complete_review()
        
        review2 = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee3.id,
            'review_date': date.today(),
            'score': 8.0,
        })
        review2.action_start_review()
        review2.action_complete_review()
        
        # Promedio debería ser (6 + 8) / 2 = 7
        self.assertEqual(self.employee1.average_score, 7.0)

    def test_10_last_review_computed_fields(self):
        """Test: Campos computados de última evaluación"""
        today = date.today()
        
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': today,
            'score': 9.0,
        })
        review.action_start_review()
        review.action_complete_review()
        
        # Verificar campos computados
        self.assertEqual(self.employee1.last_review_date, today)
        self.assertEqual(self.employee1.last_review_score, 9.0)

    def test_11_department_relation(self):
        """Test: Relación con departamento a través del empleado"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 7.0,
        })
        
        # Departamento debería heredarse del empleado
        self.assertEqual(review.department_id, self.employee1.department_id)
        self.assertEqual(review.department_id, self.department)

    def test_12_kanban_state_computed(self):
        """Test: Estado kanban calculado correctamente"""
        review = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee2.id,
            'review_date': date.today(),
            'score': 7.0,
        })
        
        # Estado normal en borrador
        self.assertEqual(review.kanban_state, 'normal')
        
        # Completar evaluación
        review.action_start_review()
        review.action_complete_review()
        self.assertEqual(review.kanban_state, 'done')
        
        # Crear otra y cancelar
        review2 = self.review_model.create({
            'employee_id': self.employee1.id,
            'reviewer_id': self.employee3.id,
            'review_date': date.today(),
            'score': 5.0,
        })
        review2.action_cancel_review()
        self.assertEqual(review2.kanban_state, 'blocked')

    def test_13_action_view_performance_reviews(self):
        """Test: Acción de ver evaluaciones desde empleado"""
        action = self.employee1.action_view_performance_reviews()
        
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'hr.performance.review')
        self.assertIn(('employee_id', '=', self.employee1.id), action['domain'])

