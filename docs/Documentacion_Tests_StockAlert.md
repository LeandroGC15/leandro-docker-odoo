# Documentación del Módulo Inventario - Alertas de Stock Crítico

Esta guía documenta el módulo `stock_critical_alert` para Odoo 17, su funcionamiento y cómo ejecutar las pruebas automatizadas.

---

## 1. Descripción del Módulo

### Información General

| Campo | Valor |
|-------|-------|
| **Nombre Técnico** | `stock_critical_alert` |
| **Nombre Funcional** | Inventario - Alertas de Stock Crítico |
| **Versión** | 17.0.1.0.0 |
| **Categoría** | Inventory |
| **Dependencias** | `base`, `stock`, `mail`, `product` |

### Funcionalidades

El módulo permite:

- ✅ Definir un stock mínimo por producto (umbral crítico)
- ✅ Generación automática de alertas cuando el stock disponible cae por debajo del umbral configurado
- ✅ Notificaciones vía `mail.message` a usuarios responsables
- ✅ Vista de tablero con productos en estado crítico agrupados por categoría
- ✅ Evita duplicados de alertas para el mismo producto (control inteligente)
- ✅ Estados de alerta: Abierta → Resuelta / Cancelada
- ✅ Auto-resolución de alertas cuando el stock se normaliza (vía cron)
- ✅ Campo calculado para identificar productos en estado crítico

---

## 2. Modelos del Módulo

### 2.1 Extensión de `product.template`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `stock_minimum` | Float | Cantidad mínima de stock (umbral de alerta) |
| `is_stock_critical` | Boolean (computed) | Indica si el stock actual está por debajo del mínimo |
| `stock_alert_ids` | One2many | Historial de alertas de stock del producto |
| `stock_alert_count` | Integer (computed) | Cantidad de alertas asociadas |

#### Lógica de `is_stock_critical`

```python
is_stock_critical = stock_minimum > 0 AND qty_available < stock_minimum
```

Un producto se considera crítico cuando:
1. Tiene configurado un stock mínimo mayor a 0
2. Su cantidad disponible (`qty_available`) es menor al mínimo

### 2.2 `stock.critical.alert` (Alerta de Stock Crítico)

Modelo principal para gestionar las alertas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `product_tmpl_id` | Many2one | Producto asociado a la alerta |
| `product_id` | Many2one (computed) | Variante del producto |
| `category_id` | Many2one (related) | Categoría del producto |
| `display_name` | Char (computed) | Nombre descriptivo de la alerta |
| `state` | Selection | Estado: `open`, `resolved`, `cancelled` |
| `stock_minimum` | Float (related) | Stock mínimo del producto |
| `qty_available_at_alert` | Float | Stock al momento de crear la alerta |
| `current_qty_available` | Float (related) | Stock actual del producto |
| `deficit` | Float (computed) | Diferencia entre mínimo y actual |
| `resolution_date` | Datetime | Fecha de resolución |
| `resolution_notes` | Text | Notas de resolución |
| `active` | Boolean | Activo (para archivar alertas) |

#### Estados del Flujo de Trabajo

```
┌─────────┐     ┌───────────┐
│  Open   │ ──▶ │ Resolved  │
└─────────┘     └───────────┘
     │
     │
     ▼
┌───────────┐
│ Cancelled │
└───────────┘

Desde Resolved o Cancelled se puede reabrir → Open
```

#### Métodos Principales

| Método | Descripción |
|--------|-------------|
| `create_alert_if_not_exists(product_tmpl)` | Crea alerta solo si no existe una abierta |
| `action_resolve()` | Marca la alerta como resuelta |
| `action_cancel()` | Cancela la alerta |
| `action_reopen()` | Reabre la alerta |
| `_send_alert_notification()` | Envía notificación vía mail.message |
| `_cron_check_stock_alerts()` | Job programado para verificar stock |
| `get_critical_products_dashboard_data()` | Datos para dashboard agrupados por categoría |

### 2.3 Extensión de `stock.picking`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `country_code` | Char (related) | Código de país de la compañía (requerido por stock_account) |

---

## 3. Cron Job Automático

El módulo incluye un cron job que se ejecuta automáticamente para:

1. **Verificar stock de productos**: Busca todos los productos con `stock_minimum > 0` y tipo `product` (almacenables)
2. **Crear alertas**: Si `qty_available < stock_minimum`, crea una alerta (si no existe una abierta)
3. **Auto-resolver alertas**: Si una alerta abierta corresponde a un producto cuyo stock ya se normalizó, la resuelve automáticamente

---

## 4. Ejecución de Tests

### 4.1 Comando Directo (Sin Reporte PDF)

Si solo deseas verificar que los tests pasan y ver los resultados en la consola, ejecuta:

```bash
docker compose -f docker-compose.db.yml up -d && \
docker compose -f docker-compose.app.yml run --rm proj \
  odoo -i stock_critical_alert \
       --test-enable \
       --stop-after-init \
       -d test_stock_alert_clean \
       --http-port=8097 \
       --test-tags=/stock_critical_alert
```

#### Explicación de parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `-i stock_critical_alert` | Instala/Actualiza el módulo |
| `--test-enable` | Habilita la ejecución de tests tras la instalación |
| `--stop-after-init` | Detiene el servidor Odoo una vez terminados los tests |
| `-d test_stock_alert_clean` | Usa una base de datos específica para pruebas |
| `--http-port=8097` | Puerto HTTP alternativo (evita conflictos) |
| `--test-tags=/stock_critical_alert` | Ejecuta **solo** los tests de este módulo |

### 4.2 Generación de Reporte QA Automático (Recomendado)

Hemos creado un script automatizado `qa_stock_alert.sh` que simplifica todo el proceso:

1. Actualiza el código de pruebas en el contenedor
2. Ejecuta los tests
3. **Descarga automáticamente el reporte PDF** a tu carpeta actual

#### Ejecución

```bash
./qa_stock_alert.sh
```

#### Resultado

Al finalizar, encontrarás un archivo llamado **`reporte_qa_stock_alert_mas_reciente.pdf`** en la carpeta raíz del proyecto. Este archivo contiene:

- ✅ Resumen ejecutivo (Status Pass/Fail)
- ✅ Estadísticas (Tiempo, número de tests)
- ✅ Lista detallada de todas las pruebas ejecutadas
- ✅ Detalle de errores (si los hubiera)

---

## 5. Lista de Pruebas Unitarias

El módulo incluye **15 tests** que validan toda la funcionalidad:

| # | Test | Descripción |
|---|------|-------------|
| 01 | `test_01_product_stock_minimum_field` | Verificar que el campo `stock_minimum` existe y funciona |
| 02 | `test_02_is_stock_critical_computation` | Verificar cálculo de `is_stock_critical` |
| 03 | `test_03_create_alert` | Crear alerta de stock crítico |
| 04 | `test_04_no_duplicate_alerts` | No se generan alertas duplicadas para el mismo producto |
| 05 | `test_05_allow_new_alert_after_resolution` | Se puede crear nueva alerta después de resolver la anterior |
| 06 | `test_06_alert_states_transitions` | Transiciones de estado de alertas |
| 07 | `test_07_deficit_computation` | Verificar cálculo del déficit |
| 08 | `test_08_cron_creates_alerts` | El cron genera alertas para productos críticos |
| 09 | `test_09_cron_no_duplicate_on_rerun` | El cron no crea duplicados al ejecutarse múltiples veces |
| 10 | `test_10_alert_display_name` | Verificar generación del `display_name` |
| 11 | `test_11_category_grouping` | Verificar que las alertas se pueden agrupar por categoría |
| 12 | `test_12_mail_message_creation` | Verificar que se crea mensaje en `mail.message` |
| 13 | `test_13_product_alert_count` | Verificar contador de alertas en producto |
| 14 | `test_14_search_critical_products` | Buscar productos con stock crítico |
| 15 | `test_15_inactive_alert_allows_new` | Una alerta inactiva permite crear nueva |

### Cobertura de Tests

| Área | Cobertura |
|------|-----------|
| Campos de `product.template` | ✅ Completa |
| Campos calculados (`is_stock_critical`, `deficit`) | ✅ Completa |
| Creación y prevención de duplicados | ✅ Completa |
| Transiciones de estado | ✅ Completa |
| Cron job | ✅ Completa |
| Notificaciones mail.message | ✅ Completa |
| Búsqueda de productos críticos | ✅ Completa |

---

## 6. Archivos del Sistema de QA

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `qa_stock_alert.sh` | Raíz del proyecto | Script bash orquestador |
| `run_tests_stock_alert_with_report.py` | Raíz del proyecto | Script Python generador de reportes |
| `test_stock_critical_alert.py` | `tests/` del módulo | Casos de prueba unitarios |

---

## 7. Resumen de Comandos

| Acción | Comando | Resultado |
|--------|---------|-----------|
| **Desarrollo Rápido** | `docker exec ...` (ver sección 4.1) | Feedback inmediato en consola |
| **Entrega / QA** | `./qa_stock_alert.sh` | Archivo PDF profesional |

---

## 8. Troubleshooting

### Error: "No se encontró ningún reporte PDF"

1. Verifica que el contenedor `proj` esté corriendo: `docker ps`
2. Verifica que el módulo esté instalado correctamente
3. Revisa los logs del contenedor: `docker logs proj`

### Error: "Module stock_critical_alert not found"

1. Verifica que el módulo esté en el path de addons de Odoo
2. Actualiza la lista de módulos en Odoo (Modo Debug → Actualizar lista de aplicaciones)

### Error en tests: Dependencias faltantes

Revisa que las dependencias (`stock`, `mail`, `product`) estén instaladas en la base de datos de pruebas.

### Alerta no se crea

1. Verifica que el producto tenga `stock_minimum > 0`
2. Verifica que el producto sea de tipo `product` (almacenable)
3. Verifica que no exista ya una alerta abierta para ese producto

---

## 9. Ejemplos de Uso

### Configurar Stock Mínimo en un Producto

```python
product = self.env['product.template'].browse(product_id)
product.stock_minimum = 10.0  # Alerta cuando stock < 10
```

### Verificar si un Producto está Crítico

```python
if product.is_stock_critical:
    print(f"¡Alerta! {product.name} tiene stock bajo")
```

### Crear Alerta Manualmente

```python
self.env['stock.critical.alert'].create_alert_if_not_exists(product)
```

### Buscar Todos los Productos Críticos

```python
critical_products = self.env['product.template'].search([
    ('is_stock_critical', '=', True)
])
```

---

*Documentación generada: 2026-01-06*
*Versión del módulo: 17.0.1.0.0*


