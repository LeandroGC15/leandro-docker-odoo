# Documentación del Módulo Ventas - Reglas de Cross-Selling

Esta guía documenta el funcionamiento del módulo `sale_cross_selling`, cómo ejecutar las pruebas automatizadas y cómo generar reportes de calidad (QA) en formato PDF.

---

## Descripción del Módulo

El módulo **Ventas - Reglas de Cross-Selling** permite sugerir productos complementarios en pedidos de venta, mejorando la experiencia de compra y aumentando las ventas.

### Funcionalidades Principales

1. **Reglas de Cross-Selling**: Definir relaciones entre productos (ej: Laptop sugiere Mouse)
2. **Relaciones Bidireccionales**: Opción para que la sugerencia funcione en ambos sentidos
3. **Wizard Interactivo**: Al crear un pedido, se muestran sugerencias de productos complementarios
4. **Integración con Pedidos de Venta**: Añadir productos sugeridos directamente al pedido

### Modelos del Módulo

| Modelo | Descripción |
|--------|-------------|
| `product.cross.sell` | Reglas de cross-selling entre productos |
| `product.template` (ext.) | Extensión con contador de reglas |
| `sale.order` (ext.) | Lógica de detección de sugerencias |
| `cross.sell.wizard` | Wizard para mostrar y añadir productos sugeridos |

---

## Estructura del Módulo

```
sale_cross_selling/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── product_cross_sell.py    # Modelo de reglas de cross-selling
│   ├── product_template.py      # Extensión de product.template
│   └── sale_order.py            # Extensión de sale.order y sale.order.line
├── wizard/
│   ├── __init__.py
│   ├── cross_sell_wizard.py     # Wizard para sugerencias
│   └── cross_sell_wizard_views.xml
├── views/
│   ├── product_cross_sell_views.xml
│   └── product_template_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── static/
│   └── description/
│       └── icon.svg
└── tests/
    ├── __init__.py
    ├── test_product_cross_sell.py      # Tests del modelo de reglas
    └── test_sale_order_cross_sell.py   # Tests de integración con pedidos
```

---

## Pruebas Unitarias

El módulo incluye **26 pruebas unitarias** organizadas en dos archivos:

### `test_product_cross_sell.py` (12 tests)

| Test | Descripción |
|------|-------------|
| `test_01_create_cross_sell_rule` | Crear regla de cross-selling válida |
| `test_02_auto_compute_name` | Verificar que el nombre se calcula automáticamente |
| `test_03_same_product_validation` | No permitir mismo producto como origen y sugerido |
| `test_04_unique_relation_validation` | No permitir reglas duplicadas activas |
| `test_05_allow_inactive_duplicate` | Permitir duplicado si está inactivo |
| `test_06_get_cross_sell_products_simple` | Obtener productos sugeridos simples |
| `test_07_get_cross_sell_products_bidirectional` | Sugerencias bidireccionales |
| `test_08_get_cross_sell_excludes_source_products` | Excluir productos ya en la lista |
| `test_09_inactive_rules_not_returned` | Reglas inactivas no retornan sugerencias |
| `test_10_copy_rule_inactive` | Al duplicar regla, se crea inactiva |
| `test_11_product_template_cross_sell_count` | Contador de cross-sells en producto |
| `test_12_multiple_products_suggestions` | Sugerencias para múltiples productos |

### `test_sale_order_cross_sell.py` (14 tests)

| Test | Descripción |
|------|-------------|
| `test_01_has_cross_sell_suggestions_empty_order` | Pedido vacío no tiene sugerencias |
| `test_02_has_cross_sell_suggestions_with_product` | Pedido con producto tiene sugerencias |
| `test_03_no_suggestions_when_all_products_in_order` | Sin sugerencias si todos ya están |
| `test_04_action_show_wizard_empty_order` | Wizard en pedido vacío → notificación warning |
| `test_05_action_show_wizard_no_suggestions` | Wizard sin sugerencias → notificación info |
| `test_06_action_show_wizard_with_suggestions` | Wizard con sugerencias abre correctamente |
| `test_07_wizard_add_selected_products` | Añadir productos seleccionados al pedido |
| `test_08_wizard_add_without_selection_raises_error` | Error al añadir sin selección |
| `test_09_wizard_select_all` | Seleccionar todos los productos |
| `test_10_wizard_deselect_all` | Deseleccionar todos los productos |
| `test_11_cannot_add_to_confirmed_order` | No añadir productos a pedido confirmado |
| `test_12_order_update_after_adding_products` | Total se actualiza al añadir |
| `test_13_bidirectional_suggestion_in_order` | Bidireccional funciona en pedidos |
| `test_14_multiple_products_multiple_suggestions` | Múltiples productos → múltiples sugerencias |

---

## Ejecución de Tests

### Opción 1: Comando Directo (Sin Reporte PDF)

Si solo deseas verificar que los tests pasan y ver los resultados en la consola:

```bash
docker compose -f docker-compose.db.yml up -d && \
docker compose -f docker-compose.app.yml run --rm proj \
  odoo -i sale_cross_selling \
       --test-enable \
       --stop-after-init \
       -d test_cross_selling_clean \
       --http-port=8098 \
       --test-tags=/sale_cross_selling
```

#### ¿Qué hace este comando?

| Parámetro | Descripción |
|-----------|-------------|
| `-i sale_cross_selling` | Instala/Actualiza el módulo |
| `--test-enable` | Habilita la ejecución de tests |
| `--stop-after-init` | Detiene Odoo una vez terminados los tests |
| `-d test_cross_selling_clean` | Usa una base de datos específica para pruebas |
| `--test-tags=/sale_cross_selling` | Ejecuta **solo** los tests de este módulo |

---

### Opción 2: Script Automatizado con Reporte PDF (Recomendado)

Hemos creado un script automatizado `qa_cross_selling.sh` que simplifica todo el proceso:

1. Actualiza el código de pruebas en el contenedor
2. Ejecuta los tests
3. **Descarga automáticamente el reporte PDF**

#### Ejecución

Desde la carpeta raíz del proyecto (`leandro-docker-odoo`):

```bash
./qa_cross_selling.sh
```

#### Resultado

Al finalizar, encontrarás un archivo llamado **`reporte_qa_cross_selling_mas_reciente.pdf`** en la carpeta raíz del proyecto con:

- ✅ Resumen ejecutivo (Status Pass/Fail)
- 📊 Estadísticas (Tiempo, número de tests)
- 📋 Lista detallada de todas las pruebas ejecutadas
- ❌ Detalle de errores (si los hubiera)

---

## Detalles Técnicos

### Archivos del Sistema de QA

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `qa_cross_selling.sh` | Raíz del proyecto | Script Bash que orquesta la operación |
| `run_tests_cross_selling_with_report.py` | Raíz del proyecto | Script Python que ejecuta tests y genera PDF |

### Flujo del Script

```
┌──────────────────────────────────────────────────────────┐
│  1. qa_cross_selling.sh (Host)                           │
│     └─> Copia script Python al contenedor                │
├──────────────────────────────────────────────────────────┤
│  2. run_tests_cross_selling_with_report.py (Contenedor)  │
│     ├─> Ejecuta tests de Odoo                            │
│     ├─> Parsea resultados                                │
│     └─> Genera reporte PDF                               │
├──────────────────────────────────────────────────────────┤
│  3. qa_cross_selling.sh (Host)                           │
│     └─> Copia PDF al host                                │
└──────────────────────────────────────────────────────────┘
```

### Funciones del Script Python

| Función | Descripción |
|---------|-------------|
| `run_odoo_tests()` | Ejecuta Odoo con flags de testing |
| `parse_test_results()` | Analiza logs y extrae estadísticas |
| `generate_pdf_report()` | Genera el documento PDF con ReportLab |

---

## Uso del Módulo

### 1. Crear Regla de Cross-Selling

1. Ve a **Ventas > Configuración > Cross-Selling**
2. Crea una nueva regla:
   - **Producto Origen**: El producto que dispara la sugerencia
   - **Producto Sugerido**: El producto complementario
   - **Bidireccional**: Marca si la relación aplica en ambos sentidos
   - **Activo**: Marca para activar la regla

### 2. Ver Sugerencias en Pedido de Venta

1. Crea o edita un pedido de venta
2. Añade productos al pedido
3. Si existen reglas de cross-selling, aparecerá el botón **"Ver Sugerencias"**
4. Selecciona los productos complementarios que deseas añadir
5. Confirma para agregarlos al pedido

---

## Dependencias

- `base`: Módulo base de Odoo
- `sale`: Módulo de ventas
- `product`: Módulo de productos

---

## Información del Módulo

| Campo | Valor |
|-------|-------|
| **Versión Odoo** | 17.0 |
| **Versión Módulo** | 17.0.1.0.0 |
| **Autor** | Binaural |
| **Licencia** | LGPL-3 |

---

## Resumen de Comandos

| Acción | Comando | Resultado |
|--------|---------|-----------|
| **Desarrollo Rápido** | Comando directo de Odoo | Feedback inmediato en consola |
| **Entrega / QA** | `./qa_cross_selling.sh` | Archivo PDF profesional para documentación |

