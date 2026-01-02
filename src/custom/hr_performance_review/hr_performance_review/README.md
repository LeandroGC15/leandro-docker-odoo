# RRHH - Evaluaciones de Desempeño

## Descripción

Módulo de Odoo 17 para la gestión de evaluaciones de desempeño de empleados. Permite crear un flujo completo de evaluaciones periódicas con seguimiento por estados, calificaciones numéricas, observaciones cualitativas y reportes PDF.

## Características

### Modelo Principal: `hr.performance.review`

- **employee_id**: Empleado evaluado (Many2one a hr.employee)
- **reviewer_id**: Evaluador que realiza la evaluación (Many2one a hr.employee)
- **review_date**: Fecha de la evaluación
- **score**: Calificación numérica (0-10)
- **comments**: Observaciones cualitativas
- **goals_next_period**: Objetivos para el siguiente ciclo
- **strengths**: Fortalezas identificadas
- **weaknesses**: Áreas de mejora

### Flujo de Trabajo

1. **Borrador**: Evaluación creada pero no iniciada
2. **En Progreso**: Evaluación en proceso de revisión
3. **Completada**: Evaluación finalizada
4. **Cancelada**: Evaluación cancelada

### Vistas Disponibles

- **Vista Kanban**: Seguimiento visual de evaluaciones por estado
- **Vista Lista**: Listado completo con información resumida
- **Vista Formulario**: Detalle completo de la evaluación

### Extensión de Empleados

El módulo extiende `hr.employee` agregando:
- Conteo de evaluaciones
- Última fecha de evaluación
- Última calificación
- Promedio de calificaciones
- Pestaña con historial de evaluaciones

### Reportes PDF

1. **Reporte de Evaluación Individual**: Detalle completo de una evaluación
2. **Histórico de Evaluaciones del Empleado**: Resumen y detalle de todas las evaluaciones

## Seguridad

### Grupos de Usuarios

- **Usuario / Evaluaciones de Desempeño**: Puede ver y crear evaluaciones
- **Manager / Evaluaciones de Desempeño**: Acceso completo a todas las evaluaciones

### Reglas de Registro

- Usuarios pueden ver evaluaciones donde son evaluadores o del mismo departamento
- Managers tienen acceso completo a todas las evaluaciones

## Dependencias

- `base`
- `hr`

## Instalación

1. Copiar el módulo a la carpeta de addons personalizados
2. Actualizar la lista de módulos
3. Instalar el módulo "RRHH - Evaluaciones de Desempeño"

## Pruebas

El módulo incluye pruebas unitarias que validan:

- Creación de evaluaciones
- Generación de secuencias
- Validación de calificaciones (rango 0-10)
- Restricción de auto-evaluación
- Flujo de estados
- Campos computados de empleado
- Relaciones y dependencias

Para ejecutar las pruebas:

```bash
odoo-bin -c odoo.conf -u hr_performance_review --test-enable --stop-after-init
```

## Autor

**Binaural**
- Website: https://www.binaural.dev

## Licencia

LGPL-3

