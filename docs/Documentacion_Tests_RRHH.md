# Documentación del Módulo RRHH - Evaluaciones de Desempeño

Esta guía documenta el módulo `hr_performance_review` para Odoo 17, su funcionamiento y cómo ejecutar las pruebas automatizadas.

---

## 1. Descripción del Módulo

### Información General

| Campo | Valor |
|-------|-------|
| **Nombre Técnico** | `hr_performance_review` |
| **Nombre Funcional** | RRHH - Evaluaciones de Desempeño |
| **Versión** | 17.0.1.0.0 |
| **Categoría** | Human Resources |
| **Dependencias** | `base`, `hr`, `mail` |

### Funcionalidades

El módulo permite:

- ✅ Crear evaluaciones de desempeño para empleados
- ✅ Asignar evaluadores y fechas de revisión
- ✅ Registrar calificaciones numéricas (0-10) y observaciones cualitativas
- ✅ Definir fortalezas, debilidades y objetivos para el siguiente período
- ✅ Seguimiento por estado (Borrador → En Progreso → Completada/Cancelada)
- ✅ Reportes PDF con histórico de evaluaciones por empleado
- ✅ Vista Kanban con estados coloreados

---

## 2. Modelos del Módulo

### 2.1 `hr.performance.review` (Evaluación de Desempeño)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Referencia automática (secuencia EVAL/XXXX) |
| `employee_id` | Many2one | Empleado evaluado |
| `reviewer_id` | Many2one | Empleado evaluador |
| `review_date` | Date | Fecha de la evaluación |
| `score` | Float | Calificación (0-10) |
| `score_percentage` | Float | Porcentaje calculado automáticamente |
| `comments` | Text | Observaciones cualitativas |
| `strengths` | Text | Fortalezas identificadas |
| `weaknesses` | Text | Áreas de mejora |
| `goals_next_period` | Text | Objetivos para el siguiente período |
| `state` | Selection | Estado del flujo de trabajo |
| `department_id` | Many2one | Departamento (heredado del empleado) |
| `job_id` | Many2one | Puesto de trabajo (heredado del empleado) |

#### Estados del Flujo de Trabajo

```
┌─────────┐     ┌─────────────┐     ┌───────────┐
│ Borrador│ ──▶ │ En Progreso │ ──▶ │ Completada│
└─────────┘     └─────────────┘     └───────────┘
     │                │
     │                │
     ▼                ▼
┌─────────┐     ┌─────────────┐
│Cancelada│ ◀── │  Cancelada  │
└─────────┘     └─────────────┘
```

#### Validaciones (Constraints)

1. **Score entre 0 y 10**: La calificación debe estar en el rango válido
2. **Evaluador ≠ Empleado**: Un empleado no puede evaluarse a sí mismo
3. **Score > 0 para completar**: No se puede completar una evaluación sin calificación

### 2.2 Extensión de `hr.employee`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `performance_review_ids` | One2many | Historial de evaluaciones |
| `performance_review_count` | Integer | Cantidad de evaluaciones |
| `last_review_date` | Date | Fecha de última evaluación completada |
| `last_review_score` | Float | Calificación de última evaluación |
| `average_score` | Float | Promedio de todas las evaluaciones completadas |
| `average_score_percentage` | Float | Porcentaje del promedio |

---

## 3. Ejecución de Tests

### 3.1 Comando Directo (Sin Reporte PDF)

Si solo deseas verificar que los tests pasan y ver los resultados en la consola, ejecuta:

```bash
docker compose -f docker-compose.db.yml up -d && \
docker compose -f docker-compose.app.yml run --rm proj \
  odoo -i hr_performance_review \
       --test-enable \
       --stop-after-init \
       -d test_rrhh_clean \
       --http-port=8098 \
       --test-tags=/hr_performance_review
```

#### Explicación de parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `-i hr_performance_review` | Instala/Actualiza el módulo |
| `--test-enable` | Habilita la ejecución de tests tras la instalación |
| `--stop-after-init` | Detiene el servidor Odoo una vez terminados los tests |
| `-d test_rrhh_clean` | Usa una base de datos específica para pruebas |
| `--http-port=8098` | Puerto HTTP alternativo (evita conflictos) |
| `--test-tags=/hr_performance_review` | Ejecuta **solo** los tests de este módulo |

### 3.2 Generación de Reporte QA Automático (Recomendado)

Hemos creado un script automatizado `qa_rrhh.sh` que simplifica todo el proceso:

1. Actualiza el código de pruebas en el contenedor
2. Ejecuta los tests
3. **Descarga automáticamente el reporte PDF** a tu carpeta actual

#### Ejecución

```bash
./qa_rrhh.sh
```

#### Resultado

Al finalizar, encontrarás un archivo llamado **`reporte_qa_rrhh_mas_reciente.pdf`** en la carpeta raíz del proyecto. Este archivo contiene:

- ✅ Resumen ejecutivo (Status Pass/Fail)
- ✅ Estadísticas (Tiempo, número de tests)
- ✅ Lista detallada de todas las pruebas ejecutadas
- ✅ Detalle de errores (si los hubiera)

---

## 4. Lista de Pruebas Unitarias

El módulo incluye **16 tests** que validan toda la funcionalidad:

| # | Test | Descripción |
|---|------|-------------|
| 01 | `test_01_create_performance_review` | Crear evaluación válida |
| 02 | `test_02_review_name_sequence` | Generación de secuencia automática |
| 03 | `test_03_score_validation_range` | Validación de score entre 0 y 10 |
| 04 | `test_04_employee_cannot_self_review` | Empleado no puede auto-evaluarse |
| 05 | `test_05_workflow_state_transitions` | Transiciones de estado del flujo |
| 06 | `test_06_cannot_complete_without_score` | No completar sin calificación |
| 07 | `test_07_cancel_and_reset_workflow` | Cancelar y reiniciar evaluación |
| 08 | `test_08_employee_review_relation` | Relación empleado-evaluaciones |
| 09 | `test_09_employee_average_score` | Cálculo de promedio del empleado |
| 10 | `test_10_last_review_computed_fields` | Campos de última evaluación |
| 11 | `test_11_department_relation` | Relación con departamento |
| 12 | `test_12_kanban_state_computed` | Estado kanban calculado |
| 13 | `test_13_action_view_performance_reviews` | Acción de ver evaluaciones |
| 14 | `test_14_score_percentage_computed` | Cálculo de porcentaje de score |
| 15 | `test_15_average_score_percentage_computed` | Cálculo de porcentaje promedio |
| 16 | `test_16_job_relation` | Relación con puesto de trabajo |

---

## 5. Archivos del Sistema de QA

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `qa_rrhh.sh` | Raíz del proyecto | Script bash orquestador |
| `run_tests_rrhh_with_report.py` | Raíz del proyecto | Script Python generador de reportes |
| `test_hr_performance_review.py` | `tests/` del módulo | Casos de prueba unitarios |

---

## 6. Resumen de Comandos

| Acción | Comando | Resultado |
|--------|---------|-----------|
| **Desarrollo Rápido** | `docker exec ...` (ver sección 3.1) | Feedback inmediato en consola |
| **Entrega / QA** | `./qa_rrhh.sh` | Archivo PDF profesional |

---

## 7. Troubleshooting

### Error: "No se encontró ningún reporte PDF"

1. Verifica que el contenedor `proj` esté corriendo: `docker ps`
2. Verifica que el módulo esté instalado correctamente
3. Revisa los logs del contenedor: `docker logs proj`

### Error: "Module hr_performance_review not found"

1. Verifica que el módulo esté en el path de addons de Odoo
2. Actualiza la lista de módulos en Odoo (Modo Debug → Actualizar lista de aplicaciones)

### Error en tests: ValidationError

Revisa que las dependencias (`hr`, `mail`) estén instaladas en la base de datos de pruebas.

---

*Documentación generada: 2026-01-06*
*Versión del módulo: 17.0.1.0.0*
