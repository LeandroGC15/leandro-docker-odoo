# Documentación del Módulo Punto de Venta - Programa de Fidelización

Esta guía documenta el funcionamiento del módulo `pos_loyalty_program`, cómo ejecutar las pruebas automatizadas y cómo generar reportes de calidad (QA) en formato PDF.

---

## Descripción del Módulo

El módulo **Punto de Venta - Programa de Fidelización** permite implementar un sistema de puntos de fidelización para clientes en el Punto de Venta (POS), incentivando la lealtad del cliente mediante la acumulación de puntos por cada compra.

### Funcionalidades Principales

1. **Acumulación Automática de Puntos**: Los clientes ganan puntos automáticamente al realizar compras
2. **Configuración Flexible**: Definir cuántos puntos se otorgan por cada monto de compra
3. **Múltiples Tipos de Redondeo**: Hacia abajo, hacia arriba o al más cercano
4. **Histórico de Transacciones**: Registro completo de todas las transacciones de puntos
5. **Resumen por Sesión**: Ver puntos totales otorgados en cada sesión de POS
6. **Reportes PDF**: Generar reportes del historial de puntos por cliente

### Modelos del Módulo

| Modelo | Descripción |
|--------|-------------|
| `pos.loyalty.history` | Histórico de transacciones de puntos de fidelización |
| `pos.config` (ext.) | Extensión con configuración del programa de fidelización |
| `pos.order` (ext.) | Cálculo y asignación de puntos al validar órdenes |
| `pos.session` (ext.) | Resumen de puntos otorgados por sesión |
| `res.partner` (ext.) | Campos de puntos y acciones de fidelización en clientes |

---

## Estructura del Módulo

```
pos_loyalty_program/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── pos_config.py           # Configuración del programa en POS
│   ├── pos_loyalty_history.py  # Modelo de histórico de transacciones
│   ├── pos_order.py            # Cálculo y asignación de puntos
│   ├── pos_session.py          # Resumen de puntos por sesión
│   └── res_partner.py          # Campos de fidelización en clientes
├── views/
│   ├── pos_config_views.xml           # Vista de configuración del POS
│   ├── pos_loyalty_history_views.xml  # Vistas del histórico
│   ├── pos_session_views.xml          # Vista de sesión con resumen
│   └── res_partner_views.xml          # Vista de cliente con puntos
├── report/
│   ├── pos_loyalty_report.xml         # Definición del reporte
│   └── pos_loyalty_report_template.xml # Plantilla QWeb del reporte
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── tests/
    ├── __init__.py
    └── test_pos_loyalty.py     # Tests del programa de fidelización
```

---

## Configuración del Módulo

### 1. Activar el Programa de Fidelización

1. Ve a **Punto de Venta → Configuración → Punto de Venta**
2. Selecciona o crea un punto de venta
3. En la sección **"Programa de Fidelización"**:
   - Activa **"Habilitar Programa de Fidelización"**
   - Configura los parámetros

### 2. Parámetros de Configuración

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| **Habilitar Programa** | Activa/desactiva el sistema de puntos | Desactivado |
| **Puntos a Otorgar** | Cantidad de puntos por cada unidad de monto | 1.0 |
| **Monto por Punto** | Monto de compra requerido para obtener los puntos | 10.0 |
| **Tipo de Redondeo** | Cómo redondear los puntos decimales | Hacia abajo |

### 3. Fórmula de Cálculo de Puntos

```
Puntos = (Monto Total de la Orden / Monto por Punto) × Puntos a Otorgar
```

**Ejemplo:** Con configuración de 1 punto por cada $10:
- Compra de $100 → 10 puntos
- Compra de $55 → 5 puntos (con redondeo hacia abajo)
- Compra de $99 → 9 puntos (con redondeo hacia abajo)

### 4. Tipos de Redondeo

| Tipo | Descripción | Ejemplo ($95, 1pt/$10) |
|------|-------------|------------------------|
| **Hacia abajo** | Siempre redondea al entero inferior | 9.5 → 9 puntos |
| **Hacia arriba** | Siempre redondea al entero superior | 9.5 → 10 puntos |
| **Al más cercano** | Redondea al entero más cercano | 9.5 → 10 puntos |

---

## Flujo de Funcionamiento

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE FIDELIZACIÓN                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CONFIGURAR POS                                              │
│     ┌────────────────────────────────────────────┐              │
│     │ ☑ Programa de Fidelización: Habilitado     │              │
│     │ Puntos a Otorgar: 1                        │              │
│     │ Monto por Punto: $10                       │              │
│     │ Redondeo: Hacia abajo                      │              │
│     └────────────────────────────────────────────┘              │
│                          │                                      │
│                          ▼                                      │
│  2. CLIENTE COMPRA EN POS                                       │
│     ┌────────────────────────────────────────────┐              │
│     │ Cliente: Juan Pérez                        │              │
│     │ Total: $150                                │              │
│     │ Puntos calculados: 150 / 10 = 15 puntos   │              │
│     └────────────────────────────────────────────┘              │
│                          │                                      │
│                          ▼                                      │
│  3. AL PAGAR: PUNTOS SE ACUMULAN AUTOMÁTICAMENTE               │
│     ┌────────────────────────────────────────────┐              │
│     │ ★ Histórico creado (FID/0001)              │              │
│     │ ★ Puntos del cliente: 0 → 15              │              │
│     │ ★ Sesión actualizada: +15 puntos          │              │
│     └────────────────────────────────────────────┘              │
│                          │                                      │
│                          ▼                                      │
│  4. VER EN CONTACTOS                                            │
│     ┌────────────────────────────────────────────┐              │
│     │ Juan Pérez                                 │              │
│     │ ┌──────────┐                               │              │
│     │ │ ★ 15 pts │ ← Botón para ver histórico   │              │
│     │ └──────────┘                               │              │
│     │                                            │              │
│     │ Pestaña Fidelización:                      │              │
│     │ • Puntos actuales: 15                      │              │
│     │ • Total ganados: 15                        │              │
│     │ • Total canjeados: 0                       │              │
│     └────────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Interfaz de Usuario

### 1. Configuración del Punto de Venta

**Ubicación:** `Punto de Venta → Configuración → Punto de Venta`

Se añade una nueva sección "Programa de Fidelización" con:
- Toggle para habilitar/deshabilitar
- Campos de configuración de puntos
- Selector de tipo de redondeo

### 2. Ficha del Cliente (Contactos)

**Ubicación:** `Contactos → [Seleccionar cliente]`

Se añaden:
- **Smart Button "★ Puntos"**: Acceso rápido al histórico de transacciones
- **Pestaña "Fidelización"**: Resumen de puntos y acciones

| Campo | Descripción |
|-------|-------------|
| Puntos de Fidelización | Saldo actual de puntos |
| Total Puntos Ganados | Suma histórica de puntos ganados |
| Total Puntos Canjeados | Suma histórica de puntos canjeados |
| Ver Histórico | Botón para abrir el histórico completo |
| Imprimir Reporte | Botón para generar PDF del historial |

### 3. Histórico de Fidelización

**Ubicación:** `Punto de Venta → Reportes → Histórico de Fidelización`

Vista de lista con:
- Referencia (FID/0001, FID/0002...)
- Fecha de transacción
- Cliente
- Tipo (Ganados 🟢 / Canjeados 🔴 / Ajuste 🔵)
- Puntos (+/-)
- Saldo después de la transacción
- Orden POS relacionada
- Monto de la orden

**Vistas adicionales:**
- Vista Pivot para análisis de datos
- Vista Gráfico para visualización de tendencias

### 4. Sesión de POS

**Ubicación:** `Punto de Venta → Órdenes → Sesiones`

Se añaden campos:
- **Puntos Ganados**: Total de puntos otorgados en la sesión
- **Transacciones de Fidelización**: Cantidad de transacciones con puntos

---

## Pruebas Unitarias

El módulo incluye **17 pruebas unitarias** que cubren todas las funcionalidades:

### `test_pos_loyalty.py` (17 tests)

| Test | Descripción |
|------|-------------|
| `test_01_partner_loyalty_points_field` | Verificar campos de puntos en partner inicializados en 0 |
| `test_02_pos_config_loyalty_settings` | Verificar configuración de fidelización en pos.config |
| `test_03_points_calculation_basic` | Calcular puntos con configuración básica (1 pt por $10) |
| `test_04_points_calculation_custom_config` | Calcular puntos con configuración personalizada |
| `test_05_points_accumulation_on_order_paid` | Acumular puntos al validar orden de POS |
| `test_06_loyalty_history_created` | Verificar creación de histórico de puntos |
| `test_07_session_points_summary` | Verificar resumen de puntos en sesión |
| `test_08_points_rounding_floor` | Redondeo hacia abajo funciona correctamente |
| `test_09_points_rounding_ceiling` | Redondeo hacia arriba funciona correctamente |
| `test_10_points_rounding_nearest` | Redondeo al más cercano funciona correctamente |
| `test_11_loyalty_disabled` | No acumular puntos cuando está deshabilitado |
| `test_12_multiple_orders_accumulation` | Acumulación de puntos de múltiples órdenes |
| `test_13_partner_total_earned` | Verificar total de puntos ganados históricamente |
| `test_14_partner_action_view_history` | Verificar acción de ver histórico |
| `test_15_no_points_without_partner` | No acumular puntos si no hay cliente en la orden |
| `test_16_add_loyalty_points_method` | Método para añadir puntos manualmente |
| `test_17_loyalty_history_name_sequence` | Verificar secuencia de nombres en histórico |

---

## Ejecución de Tests

### Opción 1: Comando Directo (Sin Reporte PDF)

Si solo deseas verificar que los tests pasan y ver los resultados en la consola:

```bash
docker compose -f docker-compose.db.yml up -d && \
docker compose -f docker-compose.app.yml run --rm proj \
  odoo -i pos_loyalty_program \
       --test-enable \
       --stop-after-init \
       -d test_pos_loyalty_clean \
       --http-port=8098 \
       --test-tags=/pos_loyalty_program
```

#### ¿Qué hace este comando?

| Parámetro | Descripción |
|-----------|-------------|
| `-i pos_loyalty_program` | Instala/Actualiza el módulo |
| `--test-enable` | Habilita la ejecución de tests |
| `--stop-after-init` | Detiene Odoo una vez terminados los tests |
| `-d test_pos_loyalty_clean` | Usa una base de datos específica para pruebas |
| `--test-tags=/pos_loyalty_program` | Ejecuta **solo** los tests de este módulo |

---

### Opción 2: Script Automatizado con Reporte PDF (Recomendado)

El script automatizado `qa_pos_loyalty.sh` simplifica todo el proceso:

1. Actualiza el código de pruebas en el contenedor
2. Ejecuta los tests
3. **Descarga automáticamente el reporte PDF**

#### Ejecución

Desde la carpeta raíz del proyecto (`leandro-docker-odoo`):

```bash
./qa_pos_loyalty.sh
```

#### Resultado

Al finalizar, encontrarás un archivo llamado **`reporte_qa_pos_loyalty_mas_reciente.pdf`** en la carpeta raíz del proyecto con:

- ✅ Resumen ejecutivo (Status Pass/Fail)
- 📊 Estadísticas (Tiempo, número de tests)
- 📋 Lista detallada de todas las pruebas ejecutadas
- ❌ Detalle de errores (si los hubiera)

---

## Detalles Técnicos

### Archivos del Sistema de QA

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `qa_pos_loyalty.sh` | Raíz del proyecto | Script Bash que orquesta la operación |
| `run_tests_pos_loyalty_with_report.py` | Raíz del proyecto | Script Python que ejecuta tests y genera PDF |

### Flujo del Script

```
┌──────────────────────────────────────────────────────────────┐
│  1. qa_pos_loyalty.sh (Host)                                 │
│     └─> Copia script Python al contenedor                    │
├──────────────────────────────────────────────────────────────┤
│  2. run_tests_pos_loyalty_with_report.py (Contenedor)        │
│     ├─> Ejecuta tests de Odoo                                │
│     ├─> Parsea resultados                                    │
│     └─> Genera reporte PDF                                   │
├──────────────────────────────────────────────────────────────┤
│  3. qa_pos_loyalty.sh (Host)                                 │
│     └─> Copia PDF al host                                    │
└──────────────────────────────────────────────────────────────┘
```

### Funciones del Script Python

| Función | Descripción |
|---------|-------------|
| `run_odoo_tests()` | Ejecuta Odoo con flags de testing |
| `parse_test_results()` | Analiza logs y extrae estadísticas |
| `generate_pdf_report()` | Genera el documento PDF con ReportLab |

---

## Casos de Uso

### Caso 1: Configuración Inicial

1. Ve a **Punto de Venta → Configuración → Punto de Venta**
2. Selecciona el POS a configurar
3. Activa el toggle "Programa de Fidelización"
4. Configura:
   - **1 punto** por cada **$10** de compra
   - Redondeo: **Hacia abajo**
5. Guarda los cambios

### Caso 2: Cliente Realiza Compra

1. Abre la sesión del POS configurado
2. Agrega productos al carrito (ej: $150)
3. **Importante**: Selecciona un cliente
4. Procesa el pago
5. El cliente recibe automáticamente **15 puntos**

### Caso 3: Consultar Puntos del Cliente

1. Ve a **Contactos**
2. Busca al cliente
3. Observa el **Smart Button "★ Puntos"** con el total
4. Abre la pestaña **"Fidelización"** para ver:
   - Puntos actuales
   - Total histórico ganado
   - Total canjeado

### Caso 4: Generar Reporte PDF

1. Ve a **Contactos → [Cliente]**
2. En la pestaña "Fidelización", clic en **"Imprimir Reporte"**
3. Se descarga un PDF con el historial completo

---

## Tipos de Transacciones

| Tipo | Código | Descripción | Ejemplo |
|------|--------|-------------|---------|
| **Ganados** | `earned` | Puntos obtenidos por compras | +10 puntos por compra de $100 |
| **Canjeados** | `redeemed` | Puntos utilizados como beneficio | -50 puntos por descuento |
| **Ajuste** | `adjustment` | Modificación manual de puntos | +20 puntos por promoción especial |

---

## Dependencias

- `base`: Módulo base de Odoo
- `point_of_sale`: Módulo de Punto de Venta

---

## Información del Módulo

| Campo | Valor |
|-------|-------|
| **Versión Odoo** | 17.0 |
| **Versión Módulo** | 17.0.1.0.0 |
| **Autor** | Binaural |
| **Licencia** | LGPL-3 |
| **Categoría** | Point of Sale |

---

## Resumen de Comandos

| Acción | Comando | Resultado |
|--------|---------|-----------|
| **Desarrollo Rápido** | Comando directo de Odoo | Feedback inmediato en consola |
| **Entrega / QA** | `./qa_pos_loyalty.sh` | Archivo PDF profesional para documentación |

---

## Notas Importantes

1. **Cliente Requerido**: Los puntos solo se acumulan si la orden tiene un cliente asignado
2. **Configuración por POS**: Cada punto de venta puede tener su propia configuración
3. **Histórico Inmutable**: Las transacciones del histórico no se pueden editar
4. **Secuencia Automática**: Las referencias (FID/XXXX) se generan automáticamente

